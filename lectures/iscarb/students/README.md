# ISCARB Student Lecture Showcase

This folder is the **public, staff-moderated publishing surface** for approved CPIT-455 student lecture PDFs.

## Publishing rules

- Publish PDF artifacts only after course-staff review.
- Remove student IDs, private contact information, grades, answer keys, and faculty-only assessment material.
- Confirm that source figures and external material are appropriately attributed.
- Use a clear filename, for example: `Team_03_Reliability_Decision_Lecture.pdf`.
- Student submission should happen through the course-approved channel (for example Blackboard); this GitHub folder is for approved public publishing, not anonymous uploads.

To publish an approved PDF, add it to this folder **and** list its path (for example
`lectures/iscarb/students/Team_03_Reliability_Decision_Lecture.pdf`) in `iscarb_public_files` in
`curriculum/publication.json`. The site build then lists it in `iscarb-students.json`, shows it on
`iscarb-students.html`, and reveals the “Student showcase” link on the course hub. Files that are not
allowlisted are not published.
