const { execSync } = require("child_process");
const os = require("os");

function getLocalIp() {
  const nets = os.networkInterfaces();
  for (const ifaces of Object.values(nets)) {
    if (!ifaces) continue;
    for (const net of ifaces) {
      if (net.family === "IPv4" && !net.internal) {
        return net.address;
      }
    }
  }
  return null;
}

const ip = getLocalIp();
if (ip) {
  process.env.REACT_NATIVE_PACKAGER_HOSTNAME = ip;
  console.log(`\n→ IP LAN rilevato: ${ip} (Expo Go: exp://${ip}:8081)\n`);
} else {
  console.warn("\n⚠ IP LAN non rilevato — prova npm run start:tunnel\n");
}

const clear = process.argv.includes("--clear") || process.argv.includes("-c");
const tunnel = process.argv.includes("--tunnel");

const args = tunnel
  ? ["expo", "start", "--tunnel", ...(clear ? ["-c"] : [])]
  : ["expo", "start", "--lan", ...(clear ? ["-c"] : [])];
execSync(`npx ${args.join(" ")}`, { stdio: "inherit", env: process.env });
