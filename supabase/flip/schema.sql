-- CPIT-455 flipped lectures: seat booking (Supabase / Postgres).
-- No student data lives in this file or in the repository. The roster is entered directly in the database.
-- Rules enforced here, on the server:
--   * Booking and cancelling go only through book_seat() and cancel_booking(); each runs as one transaction,
--     and the seat row is locked, so two students pressing the same seat at the same moment cannot both succeed.
--   * One seat per seat row and one seat per student (UNIQUE), the student ID and university email must match the
--     roster, and registration closes 72 hours before the lecture by the server clock.
--   * Row Level Security on every table. The public key reads lectures, seats and seat_status() only;
--     roster and bookings are never readable with it.
--   * The cancellation code is stored only as a bcrypt hash and shown to the student once.
--   * admin_* functions require a signed-in user listed in admin_users whose email is arnoor@kau.edu.sa.

create extension if not exists pgcrypto with schema extensions;

create table if not exists public.lectures (
  id int primary key,
  number int not null unique,
  chapter text not null,
  title_en text not null,
  title_ar text not null,
  assignment_en text not null,
  assignment_ar text not null,
  starts_at timestamptz not null            -- entered in Riyadh time (UTC+3)
);

create table if not exists public.seats (
  id int primary key,
  lecture_id int not null references public.lectures(id) on delete cascade,
  part_no int not null check (part_no between 1 and 3),
  title_en text not null,
  title_ar text not null,
  slides text not null,
  unique (lecture_id, part_no)
);

create table if not exists public.roster (
  student_id text primary key check (student_id ~ '^[0-9]{7}$'),
  full_name text not null,
  email text not null unique check (email = lower(email))
);

create table if not exists public.bookings (
  id bigint generated always as identity primary key,
  seat_id int not null unique references public.seats(id),
  student_id text not null unique references public.roster(student_id) on delete cascade,
  entered_name text,
  cancel_code_hash text not null,
  cancel_attempts int not null default 0,
  created_at timestamptz not null default now(),
  accuracy numeric(3,2) check (accuracy in (0, 0.5, 1)),
  understanding numeric(3,2) check (understanding in (0, 0.5, 1)),
  quiz numeric(3,2) check (quiz in (0, 0.25, 0.5)),
  commitment numeric(3,2) check (commitment in (0, 0.25, 0.5))
);

create table if not exists public.admin_users (
  user_id uuid primary key
);

alter table public.lectures enable row level security;
alter table public.seats enable row level security;
alter table public.roster enable row level security;
alter table public.bookings enable row level security;
alter table public.admin_users enable row level security;

drop policy if exists lectures_read on public.lectures;
create policy lectures_read on public.lectures for select to anon, authenticated using (true);
drop policy if exists seats_read on public.seats;
create policy seats_read on public.seats for select to anon, authenticated using (true);
-- roster, bookings and admin_users have no policies: nothing is readable or writable through the API.

revoke all on public.roster, public.bookings, public.admin_users from anon, authenticated;
revoke insert, update, delete, truncate on public.lectures, public.seats from anon, authenticated;
grant select on public.lectures, public.seats to anon, authenticated;

-- Seat status only: which seat is booked and whether registration for its lecture is closed. No names or IDs.
create or replace function public.seat_status()
returns table (seat_id int, booked boolean, closed boolean)
language sql stable security definer set search_path = ''
as $$
  select s.id,
         exists (select 1 from public.bookings b where b.seat_id = s.id),
         now() >= l.starts_at - interval '72 hours'
  from public.seats s join public.lectures l on l.id = s.lecture_id
  order by s.id;
$$;

create or replace function public.flip_new_code()
returns text language plpgsql volatile set search_path = ''
as $$
declare
  alphabet constant text := 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';
  bytes bytea := extensions.gen_random_bytes(6);
  code text := '';
begin
  for i in 0..5 loop
    code := code || substr(alphabet, 1 + (get_byte(bytes, i) % length(alphabet)), 1);
  end loop;
  return code;
end;
$$;

create or replace function public.book_seat(p_student_id text, p_email text, p_full_name text, p_seat_id int)
returns jsonb language plpgsql volatile security definer set search_path = ''
as $$
declare
  v_id text := btrim(coalesce(p_student_id, ''));
  v_email text := lower(btrim(coalesce(p_email, '')));
  v_seat record;
  v_code text;
begin
  if v_id !~ '^[0-9]{7}$'
     or not exists (select 1 from public.roster r where r.student_id = v_id and r.email = v_email) then
    return jsonb_build_object('ok', false, 'error', 'not_in_roster');
  end if;
  select s.id, s.part_no, s.title_en, s.title_ar, s.slides, l.number, l.chapter, l.starts_at
    into v_seat
    from public.seats s join public.lectures l on l.id = s.lecture_id
   where s.id = p_seat_id
   for update of s;
  if not found then
    return jsonb_build_object('ok', false, 'error', 'no_seat');
  end if;
  if now() >= v_seat.starts_at - interval '72 hours' then
    return jsonb_build_object('ok', false, 'error', 'closed');
  end if;
  if exists (select 1 from public.bookings b where b.student_id = v_id) then
    return jsonb_build_object('ok', false, 'error', 'already');
  end if;
  if exists (select 1 from public.bookings b where b.seat_id = p_seat_id) then
    return jsonb_build_object('ok', false, 'error', 'taken');
  end if;
  v_code := public.flip_new_code();
  begin
    insert into public.bookings (seat_id, student_id, entered_name, cancel_code_hash)
    values (p_seat_id, v_id, left(btrim(coalesce(p_full_name, '')), 120), extensions.crypt(v_code, extensions.gen_salt('bf', 8)));
  exception when unique_violation then
    if exists (select 1 from public.bookings b where b.student_id = v_id) then
      return jsonb_build_object('ok', false, 'error', 'already');
    end if;
    return jsonb_build_object('ok', false, 'error', 'taken');
  end;
  return jsonb_build_object('ok', true, 'code', v_code, 'lecture', v_seat.number, 'chapter', v_seat.chapter,
                            'part', v_seat.part_no, 'title_en', v_seat.title_en, 'title_ar', v_seat.title_ar,
                            'slides', v_seat.slides, 'starts_at', v_seat.starts_at,
                            'draft_due', v_seat.starts_at - interval '48 hours');
end;
$$;

create or replace function public.cancel_booking(p_student_id text, p_code text)
returns jsonb language plpgsql volatile security definer set search_path = ''
as $$
declare
  v_id text := btrim(coalesce(p_student_id, ''));
  v_code text := upper(btrim(coalesce(p_code, '')));
  v_b record;
begin
  select b.id, b.cancel_code_hash, b.cancel_attempts, l.starts_at
    into v_b
    from public.bookings b join public.seats s on s.id = b.seat_id join public.lectures l on l.id = s.lecture_id
   where b.student_id = v_id
   for update of b;
  if not found then
    return jsonb_build_object('ok', false, 'error', 'bad_code');
  end if;
  if now() >= v_b.starts_at - interval '72 hours' then
    return jsonb_build_object('ok', false, 'error', 'closed');
  end if;
  if v_b.cancel_attempts >= 10 then
    return jsonb_build_object('ok', false, 'error', 'locked');
  end if;
  if extensions.crypt(v_code, v_b.cancel_code_hash) <> v_b.cancel_code_hash then
    update public.bookings set cancel_attempts = cancel_attempts + 1 where id = v_b.id;
    return jsonb_build_object('ok', false, 'error', 'bad_code');
  end if;
  delete from public.bookings where id = v_b.id;
  return jsonb_build_object('ok', true);
end;
$$;

-- ---- Administration (signed-in instructor only) ------------------------------------------------------------------
create or replace function public.flip_is_admin()
returns boolean language sql stable security definer set search_path = ''
as $$
  select auth.uid() is not null
     and exists (select 1 from public.admin_users a where a.user_id = auth.uid())
     and lower(coalesce(auth.jwt() ->> 'email', '')) = 'arnoor@kau.edu.sa';
$$;

create or replace function public.flip_require_admin()
returns void language plpgsql stable security definer set search_path = ''
as $$
begin
  if not public.flip_is_admin() then
    raise exception 'forbidden' using errcode = '42501';
  end if;
end;
$$;

create or replace function public.admin_bookings()
returns table (booking_id bigint, lecture int, chapter text, part int, seat_id int, title_en text,
               student_id text, full_name text, email text, created_at timestamptz,
               accuracy numeric, understanding numeric, quiz numeric, commitment numeric, total numeric)
language plpgsql stable security definer set search_path = ''
as $$
begin
  perform public.flip_require_admin();
  return query
  select b.id, l.number, l.chapter, s.part_no, s.id, s.title_en, r.student_id, r.full_name, r.email, b.created_at,
         b.accuracy, b.understanding, b.quiz, b.commitment,
         coalesce(b.accuracy, 0) + coalesce(b.understanding, 0) + coalesce(b.quiz, 0) + coalesce(b.commitment, 0)
    from public.bookings b
    join public.seats s on s.id = b.seat_id
    join public.lectures l on l.id = s.lecture_id
    join public.roster r on r.student_id = b.student_id
   order by l.number, s.part_no;
end;
$$;

create or replace function public.admin_roster()
returns table (student_id text, full_name text, email text, booked boolean)
language plpgsql stable security definer set search_path = ''
as $$
begin
  perform public.flip_require_admin();
  return query
  select r.student_id, r.full_name, r.email, exists (select 1 from public.bookings b where b.student_id = r.student_id)
    from public.roster r order by r.full_name;
end;
$$;

create or replace function public.admin_roster_add(p_student_id text, p_full_name text, p_email text)
returns jsonb language plpgsql volatile security definer set search_path = ''
as $$
begin
  perform public.flip_require_admin();
  insert into public.roster (student_id, full_name, email)
  values (btrim(p_student_id), btrim(p_full_name), lower(btrim(p_email)))
  on conflict (student_id) do update set full_name = excluded.full_name, email = excluded.email;
  return jsonb_build_object('ok', true);
end;
$$;

-- Adds a student to a seat, also after registration has closed. Returns a cancellation code for the student.
create or replace function public.admin_add(p_student_id text, p_seat_id int)
returns jsonb language plpgsql volatile security definer set search_path = ''
as $$
declare v_code text := public.flip_new_code();
begin
  perform public.flip_require_admin();
  perform 1 from public.seats where id = p_seat_id for update;
  if exists (select 1 from public.bookings where seat_id = p_seat_id) then
    return jsonb_build_object('ok', false, 'error', 'taken');
  end if;
  if exists (select 1 from public.bookings where student_id = btrim(p_student_id)) then
    return jsonb_build_object('ok', false, 'error', 'already');
  end if;
  insert into public.bookings (seat_id, student_id, cancel_code_hash)
  values (p_seat_id, btrim(p_student_id), extensions.crypt(v_code, extensions.gen_salt('bf', 8)));
  return jsonb_build_object('ok', true, 'code', v_code);
end;
$$;

create or replace function public.admin_move(p_booking_id bigint, p_seat_id int)
returns jsonb language plpgsql volatile security definer set search_path = ''
as $$
begin
  perform public.flip_require_admin();
  perform 1 from public.seats where id = p_seat_id for update;
  if exists (select 1 from public.bookings where seat_id = p_seat_id and id <> p_booking_id) then
    return jsonb_build_object('ok', false, 'error', 'taken');
  end if;
  update public.bookings set seat_id = p_seat_id where id = p_booking_id;
  return jsonb_build_object('ok', found);
end;
$$;

create or replace function public.admin_cancel(p_booking_id bigint)
returns jsonb language plpgsql volatile security definer set search_path = ''
as $$
begin
  perform public.flip_require_admin();
  delete from public.bookings where id = p_booking_id;
  return jsonb_build_object('ok', found);
end;
$$;

create or replace function public.admin_score(p_booking_id bigint, p_accuracy numeric, p_understanding numeric,
                                              p_quiz numeric, p_commitment numeric)
returns jsonb language plpgsql volatile security definer set search_path = ''
as $$
begin
  perform public.flip_require_admin();
  update public.bookings
     set accuracy = p_accuracy, understanding = p_understanding, quiz = p_quiz, commitment = p_commitment
   where id = p_booking_id;
  return jsonb_build_object('ok', found);
end;
$$;

-- After the final grades are recorded: delete all bookings and the roster.
create or replace function public.admin_purge(p_confirm text)
returns jsonb language plpgsql volatile security definer set search_path = ''
as $$
begin
  perform public.flip_require_admin();
  if p_confirm <> 'DELETE' then
    return jsonb_build_object('ok', false, 'error', 'confirm');
  end if;
  delete from public.bookings where true;
  delete from public.roster where true;
  return jsonb_build_object('ok', true);
end;
$$;

-- Execute rights: the public key may call only seat_status, book_seat and cancel_booking.
revoke execute on all functions in schema public from public, anon, authenticated;
grant execute on function public.seat_status() to anon, authenticated;
grant execute on function public.book_seat(text, text, text, int) to anon, authenticated;
grant execute on function public.cancel_booking(text, text) to anon, authenticated;
grant execute on function public.admin_bookings(), public.admin_roster(), public.admin_roster_add(text, text, text),
  public.admin_add(text, int), public.admin_move(bigint, int), public.admin_cancel(bigint),
  public.admin_score(bigint, numeric, numeric, numeric, numeric), public.admin_purge(text) to authenticated;
alter default privileges in schema public revoke execute on functions from public, anon, authenticated;
