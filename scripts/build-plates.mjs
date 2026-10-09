// The four zone plates, chosen off the monastery's own photographs.
//
// The earlier generated plates were architecturally wrong — whitewashed walls
// and grey shingle, when Saharna is yellow ochre with green sheet-metal roofs
// and blue as the strong secondary (design/extracted/FINDINGS.md). These are
// the real place. Re-run after changing a choice:  bun scripts/build-plates.mjs
//
// Through scripts/lib/restore.mjs (house grade), webp.
import { stat } from "node:fs/promises";
import path from "node:path";
import sharp from "sharp";
import { restore } from "./lib/restore.mjs";

const ROOT = path.resolve(import.meta.dirname, "..");
const SRC = path.join(ROOT, "design/extracted/images");
const ARCHIVE = path.resolve(ROOT, "../msaharna-archive");
const OUT = path.join(ROOT, "apps/client/public/plates");

const PLATES = [
  {
    // I · ROCK — the cave mouth cut into the cliff face. Subtraction made
    // literal: a church you make by taking stone away. The whole zone in
    // one frame. (Found by the archive session; better than the wall shot
    // I had, which was a wall with a door on it.)
    name: "rock",
    from: "media/images/2014/06/612.jpg",
    archive: true,
  },
  {
    // II · GREEN — the complex in the wooded gorge: ochre walls, green roofs,
    // the blue building. The zone's whole thesis in one frame.
    //
    // The archive offered a 2560px procession frame instead. Rejected: it is
    // a superb photograph but it is blue and white — vestments, whitewash,
    // gold domes — and Zone II is gorge green with ochre buildings inside.
    // Resolution does not outrank being the right colour.
    name: "green",
    from: "complex-overview/1011.jpg",
  },
  {
    // III · GOLD & PALL — the relics buried in fresh flowers, thread gold,
    // hanging lamps. The pink and crimson are the living half of the palette
    // and must not be tidied into earth tones.
    //
    // The archive offered a 4496px D5300 frame described as "relics in fresh
    // flowers". It is not: it is an outdoor procession in daylight past a
    // green roof, with petals on the grass. Zone III does not move and is not
    // outdoors. Rejected on subject.
    name: "gold-door",
    from: "relics-macarie/1010.jpg",
  },
  {
    // IV · RIVER — the Nistru from the cliff above, with the far bank and the
    // limestone scar. The archive was said to hold no river frame; it does.
    name: "river",
    from: "complex-overview/1201.jpg",
  },
];

for (const plate of PLATES) {
  const source = plate.archive ? path.join(ARCHIVE, plate.from) : path.join(SRC, plate.from);
  const target = path.join(OUT, `${plate.name}.webp`);

  await restore(source, [{ file: target, width: 1920, quality: 82 }], { force: true });

  const { width, height } = await sharp(target).metadata();
  const { size } = await stat(target);
  console.log(
    `${plate.name.padEnd(10)} ${plate.from.padEnd(38)} ${width}x${height}  ${Math.round((size ?? 0) / 1024)}KB`,
  );
}
