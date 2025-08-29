import { Game } from 'src/types/game';

export function wonLostGames(games: Game[]) {
  let won = 0;
  let lost = 0;

  games.forEach((game) => {
    if (game.gained_lost > 0) {
      won++;
    } else {
      lost++;
    }
  });
  return { won, lost };
}
