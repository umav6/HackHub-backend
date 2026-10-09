import EventPoster from "./EventPoster";

const PALETTES = [
  ["#0d9488", "#134e4a"],
  ["#0f766e", "#164e63"],
  ["#14b8a6", "#0f766e"],
  ["#0e7490", "#1e3a5f"],
  ["#0d9488", "#365314"],
  ["#115e59", "#312e81"],
];

function EventPoster({ event }) {
  const [from, to] = PALETTES[event.id % PALETTES.length];
  const dateLabel = new Date(event.date).toLocaleDateString("en-IN", {
    day: "numeric", month: "short", year: "numeric",
  });

  return (
    <div className="poster" style={{ background: `linear-gradient(160deg, ${from}, ${to})` }}>
      <span className="poster-circle poster-circle-1" />
      <span className="poster-circle poster-circle-2" />
      <p className="poster-tag">{event.mode.toUpperCase()} EVENT</p>
      <h3 className="poster-title">{event.name}</h3>
      <p className="poster-org">{event.organizer}</p>
      <div className="poster-footer">
        <p>{dateLabel}</p>
        <p>{event.location}</p>
        <p className="poster-prize">Prize pool {event.prizePool}</p>
      </div>
    </div>
  );
}

export default EventPoster;