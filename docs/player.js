// Wires up the Shuffle and Sleep mix buttons on the homepage.
//
// Shuffle: pick a random story with audio, open its page with ?autoplay=1.
// Sleep mix: shuffle the story list, take the first MIX_STORY_COUNT stories,
//   then open mix.html with the queue in the URL.

const MIX_STORY_COUNT = 6;

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
  return shuffleInPlace(stories.slice()).slice(0, MIX_STORY_COUNT);
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
