// Wires up the Shuffle and Sleep mix buttons on the homepage.
//
// Shuffle: pick a random story with audio, open its page with ?autoplay=1.
// Sleep mix: shuffle the story list, greedily fit stories toward a 1-hour
//   target, then open mix.html with the queue in the URL.

const MIX_TARGET_SECONDS = 60 * 60;
const MIX_OVERSHOOT_TOLERANCE = 5 * 60;

function pickRandom(items) {
  return items[Math.floor(Math.random() * items.length)];
}

function shuffleInPlace(items) {
  for (let i = items.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [items[i], items[j]] = [items[j], items[i]];
  }
  return items;
}

function buildSleepMix(stories) {
  const shuffled = shuffleInPlace(stories.slice());
  const queue = [];
  let total = 0;
  for (const story of shuffled) {
    const next = total + (story.duration || 0);
    if (queue.length > 0 && next > MIX_TARGET_SECONDS + MIX_OVERSHOOT_TOLERANCE) {
      continue;
    }
    queue.push(story);
    total = next;
    if (total >= MIX_TARGET_SECONDS) break;
  }
  return queue;
}

async function init() {
  let stories;
  try {
    const response = await fetch('stories.json');
    stories = await response.json();
  } catch (err) {
    console.error('Could not load stories.json', err);
    return;
  }

  const playable = stories.filter(s => s.audio);
  if (playable.length === 0) return;

  const shuffleButton = document.getElementById('shuffle-button');
  const mixButton = document.getElementById('sleep-mix-button');

  if (shuffleButton) {
    shuffleButton.addEventListener('click', () => {
      const story = pickRandom(playable);
      location.href = story.url + '?autoplay=1';
    });
  }

  if (mixButton) {
    mixButton.addEventListener('click', () => {
      const queue = buildSleepMix(playable);
      if (queue.length === 0) return;
      const slugs = queue.map(s => s.slug).join(',');
      location.href = 'mix.html?q=' + encodeURIComponent(slugs);
    });
  }
}

document.addEventListener('DOMContentLoaded', init);
