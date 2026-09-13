// Compatibility entry point. Every chapter is authored independently; never
// synthesize Chapter 11 by replacing words in the Chapter 10 assignment.
import {spawnSync} from 'node:child_process';
const result=spawnSync('python',['tools/build_classroom.py'],{stdio:'inherit'});
if(result.error)throw result.error;
process.exit(result.status??1);
