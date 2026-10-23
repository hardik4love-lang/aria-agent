export interface BookingSlot {
  startUtc: string;
  endUtc: string;
  timeZone: string;
}

export function normalizeBookingInterval(slot: BookingSlot) {
  const startEpoch = new Date(slot.startUtc).getTime();
  const endEpoch = new Date(slot.endUtc).getTime();
  const durationMinutes = Math.round((endEpoch - startEpoch) / (60 * 1000));

  const dtf = new Intl.DateTimeFormat("en-US", {
    timeZone: slot.timeZone,
    dateStyle: "medium",
    timeStyle: "short",
  });

  const formattedLocalStart = dtf.format(new Date(startEpoch));
  const isDstActive = checkIsDst(new Date(startEpoch), slot.timeZone);

  return {
    utcStartEpoch: startEpoch,
    utcEndEpoch: endEpoch,
    durationMinutes,
    formattedLocalStart,
    isDstActive,
  };
}

function checkIsDst(d: Date, tz: string): boolean {
  const jan = new Date(d.getFullYear(), 0, 1);
  const jul = new Date(d.getFullYear(), 6, 1);
  return d.getTimezoneOffset() < Math.max(jan.getTimezoneOffset(), jul.getTimezoneOffset());
}
