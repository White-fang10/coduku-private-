-- Judge0 Language Patches for WSL2/Windows
-- Runs after Judge0 seeds its default language table
-- Fixes: Java (JVM heap), JavaScript/TypeScript (Node18), removes Kotlin/Go

-- Java: use cd /box so classpath resolves, limit heap to fit WSL2 sandbox
UPDATE languages SET
  compile_cmd = '/usr/local/openjdk13/bin/javac %s Main.java',
  run_cmd     = 'cd /box && /usr/local/openjdk13/bin/java -Xmx128m -Xms16m -XX:+UseSerialGC -XX:TieredStopAtLevel=1 -XX:ReservedCodeCacheSize=32m Main'
WHERE id = 62;

-- JavaScript: use Node 18 (Node 12 crashes with SIGILL in WSL2 isolate)
UPDATE languages SET
  run_cmd = '/usr/bin/node18 script.js'
WHERE id = 63;

-- TypeScript: use Node 18 for execution
UPDATE languages SET
  compile_cmd = '/usr/bin/tsc %s script.ts',
  run_cmd     = '/usr/bin/node18 script.js'
WHERE id = 74;

-- Archive Kotlin and Go (broken on WSL2 due to JVM/CGO thread limits)
UPDATE languages SET is_archived = true WHERE id IN (60, 78);
