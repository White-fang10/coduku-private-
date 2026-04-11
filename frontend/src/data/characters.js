// ── Shared character data ──────────────────────────────────────────────────
// Single source of truth for character images, imported by both
// SortingCeremony.js (for the ceremony UI) and App.js (for the navbar avatar).

import char1  from '../assets/characters/char1.png';
import char2  from '../assets/characters/char2.png';
import char3  from '../assets/characters/char3.png';
import char4  from '../assets/characters/char4.png';
import char5  from '../assets/characters/char5.png';
import char6  from '../assets/characters/char6.png';
import char7  from '../assets/characters/char7.png';
import char8  from '../assets/characters/char8.png';
import char9  from '../assets/characters/char9.png';
import char10 from '../assets/characters/char10.png';
import char11 from '../assets/characters/char11.png';
import char12 from '../assets/characters/char12.png';
import char13 from '../assets/characters/char13.png';
import char14 from '../assets/characters/char14.png';
import char15 from '../assets/characters/char15.png';

export const CHARACTERS = [
  { id: 1,  name: 'Char 1',  src: char1,  color: '#c84b31' },
  { id: 2,  name: 'Char 2',  src: char2,  color: '#4a90d9' },
  { id: 3,  name: 'Char 3',  src: char3,  color: '#e8a800' },
  { id: 4,  name: 'Char 4',  src: char4,  color: '#2ecc71' },
  { id: 5,  name: 'Char 5',  src: char5,  color: '#9b59b6' },
  { id: 6,  name: 'Char 6',  src: char6,  color: '#e74c3c' },
  { id: 7,  name: 'Char 7',  src: char7,  color: '#27ae60' },
  { id: 8,  name: 'Char 8',  src: char8,  color: '#f39c12' },
  { id: 9,  name: 'Char 9',  src: char9,  color: '#8e44ad' },
  { id: 10, name: 'Char 10', src: char10, color: '#16a085' },
  { id: 11, name: 'Char 11', src: char11, color: '#2980b9' },
  { id: 12, name: 'Char 12', src: char12, color: '#e67e22' },
  { id: 13, name: 'Char 13', src: char13, color: '#1abc9c' },
  { id: 14, name: 'Char 14', src: char14, color: '#d35400' },
  { id: 15, name: 'Char 15', src: char15, color: '#8e44ad' },
];

/** Look up a character's imported image URL by its numeric id (1-15). */
export const CHAR_SRCS = Object.fromEntries(CHARACTERS.map(c => [c.id, c.src]));
