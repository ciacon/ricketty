# Ricketty design

Ricketty is a local, fullscreen Textual dashboard. Its renderer is deliberately
separate from data collection: widgets never perform local probes or network I/O.

## Runtime ownership

1. Each provider returns an immutable `StatusSnapshot` containing a source,
   severity, timezone-aware observation time, monotonic observation time, and
   display message.
2. `Scheduler` owns one periodic task per provider in an `asyncio.TaskGroup`.
   It schedules from monotonic deadlines, so provider work duration does not
   accumulate cadence drift.
3. A bounded queue coalesces pending updates. When the UI is behind, the newest
   snapshot replaces stale queued data.
4. `RickettyApp` consumes that queue on Textual's event loop and updates the
   matching clock, system, or bulletin panel. Unknown sources appear in the
   event log.
5. A provider exception becomes an error snapshot. One broken source degrades
   its panel rather than stopping the dashboard.

The boot ticker is intentionally separate from normal status updates. It is
cancellable and slow for effect; it must not block the clock or provider tasks.

## Boundaries

v0.1 uses only local, offline sources: wall-clock time, Linux uptime, home
filesystem free space, and bundled sample bulletins. It has no HTTP listener,
network fetches, database, credentials, account login, or Hermes integration.

Subinterpreters are not v0.1 infrastructure. Any future experiment belongs
outside the dashboard's critical path and must demonstrate a measured benefit.
