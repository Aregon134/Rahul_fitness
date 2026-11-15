// Playground has no CLI host option. Bind its implicit HTTP listeners to loopback.
const net = require('node:net');
const assert = require('node:assert/strict');
const listen = net.Server.prototype.listen;
net.Server.prototype.listen = function (...args) {
  if (typeof args[0] === 'number' && typeof args[1] !== 'string') args.splice(1, 0, '127.0.0.1');
  else if (args[0] && typeof args[0] === 'object' && 'port' in args[0]) args[0] = {...args[0], host: '127.0.0.1'};
  return Reflect.apply(listen, this, args);
};
if (require.main === module) {
  const probe = net.createServer();
  probe.listen(0, () => {
    assert.equal(probe.address().address, '127.0.0.1');
    probe.close(() => process.stdout.write('PASS: preview listeners bind to localhost.\n'));
  });
}
