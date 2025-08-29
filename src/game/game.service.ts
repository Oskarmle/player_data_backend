import { Injectable } from '@nestjs/common';
import { Repository } from 'typeorm';
import { Game } from './entities/game.entity';
import { InjectRepository } from '@nestjs/typeorm';
import { wonLostGames } from 'src/calculations/wonLostGames';

@Injectable()
export class GameService {
  constructor(
    @InjectRepository(Game)
    private gameRepository: Repository<Game>,
  ) {}

  findAll() {
    return this.gameRepository.find({ relations: ['player'] });
    // return this.gameRepository.find();
  }

  findOne(game_id: string) {
    return this.gameRepository.findOne({
      where: { game_id: game_id },
      relations: ['player'],
    });
  }

  findPlayerGames(player_id: string) {
    return this.gameRepository.find({
      where: { player: { player_id: player_id } },
    });
  }

  async findUserGames(userId: string) {
    return this.gameRepository.find({
      where: {
        player: {
          user: {
            user_id: userId,
          },
        },
      },
    });
  }

  async gamesStatsUser(userId: string) {
    const games = await this.findUserGames(userId);
    const gamesForCalc = games.map((game) => ({
      ...game,
      game_date:
        game.game_date instanceof Date
          ? game.game_date.toISOString()
          : game.game_date,
    }));
    const { won, lost } = wonLostGames(gamesForCalc);
    return {
      won,
      lost,
      totalGames: won + lost,
      winRate: (won / (won + lost)) * 100,
    };
  }

  async gamesStatsPlayer(playerId: string) {
    const games = await this.findPlayerGames(playerId);
    const gamesForCalc = games.map((game) => ({
      ...game,
      game_date:
        game.game_date instanceof Date
          ? game.game_date.toISOString()
          : game.game_date,
    }));
    const { won, lost } = wonLostGames(gamesForCalc);
    return {
      won,
      lost,
      totalGames: won + lost,
      winRate: (won / (won + lost)) * 100,
    };
  }
}
