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
      winRate: ((won / (won + lost)) * 100).toFixed(1),
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
      winRate: ((won / (won + lost)) * 100).toFixed(1),
    };
  }

  async playerRatingEachMonth(playerId: string) {
    const games = await this.findPlayerGames(playerId);

    // Sort games by date
    const sortedGames = [...games].sort(
      (a, b) =>
        new Date(a.game_date).getTime() - new Date(b.game_date).getTime(),
    );

    // Map to hold monthly aggregated stats
    const monthlyMap: Record<
      string,
      {
        lastRating: number;
        totalGainedLost: number;
        totalRating: number;
        gamesPlayed: number;
        won: number;
        lost: number;
      }
    > = {};

    sortedGames.forEach((game) => {
      const date = new Date(game.game_date);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;

      if (!monthlyMap[monthKey]) {
        monthlyMap[monthKey] = {
          lastRating: 0,
          totalGainedLost: 0,
          totalRating: 0,
          gamesPlayed: 0,
          won: 0,
          lost: 0,
        };
      }

      monthlyMap[monthKey].lastRating = game.player_rating;
      monthlyMap[monthKey].totalGainedLost += game.gained_lost;
      monthlyMap[monthKey].totalRating += game.player_rating;
      monthlyMap[monthKey].gamesPlayed += 1;

      if (game.gained_lost > 0) {
        monthlyMap[monthKey].won += 1;
      } else if (game.gained_lost < 0) {
        monthlyMap[monthKey].lost += 1;
      }
    });

    // Convert to array and compute averages
    return Object.entries(monthlyMap).map(([month, stats]) => ({
      month,
      lastRating: stats.lastRating,
      totalGainedLost: stats.totalGainedLost,
      gamesPlayed: stats.gamesPlayed,
      averageRatingOpponent: stats.totalRating / stats.gamesPlayed,
      won: stats.won,
      lost: stats.lost,
    }));
  }

  async userRatingEachMonth(userId: string) {
    const games = await this.findUserGames(userId);

    // Sort games by date
    const sortedGames = [...games].sort(
      (a, b) =>
        new Date(a.game_date).getTime() - new Date(b.game_date).getTime(),
    );

    // Map to hold monthly aggregated stats
    const monthlyMap: Record<
      string,
      {
        lastRating: number;
        totalGainedLost: number;
        totalRating: number;
        gamesPlayed: number;
        won: number;
        lost: number;
      }
    > = {};

    sortedGames.forEach((game) => {
      const date = new Date(game.game_date);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;

      if (!monthlyMap[monthKey]) {
        monthlyMap[monthKey] = {
          lastRating: 0,
          totalGainedLost: 0,
          totalRating: 0,
          gamesPlayed: 0,
          won: 0,
          lost: 0,
        };
      }

      monthlyMap[monthKey].lastRating = game.player_rating;
      monthlyMap[monthKey].totalGainedLost += game.gained_lost;
      monthlyMap[monthKey].totalRating += game.player_rating;
      monthlyMap[monthKey].gamesPlayed += 1;

      if (game.gained_lost > 0) {
        monthlyMap[monthKey].won += 1;
      } else if (game.gained_lost < 0) {
        monthlyMap[monthKey].lost += 1;
      }
    });

    // Convert to array and compute averages
    return Object.entries(monthlyMap).map(([month, stats]) => ({
      month,
      lastRating: stats.lastRating,
      totalGainedLost: stats.totalGainedLost,
      gamesPlayed: stats.gamesPlayed,
      averageRatingOpponent: stats.totalRating / stats.gamesPlayed,
      won: stats.won,
      lost: stats.lost,
    }));
  }
}
