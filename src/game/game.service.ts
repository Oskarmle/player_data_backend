import { Injectable } from '@nestjs/common';
import { Repository } from 'typeorm';
import { Game } from './entities/game.entity';
import { InjectRepository } from '@nestjs/typeorm';

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

  findByPlayerId(player_id: string) {
    return this.gameRepository.find({
      where: { player: { player_id: player_id } },
      relations: ['player'],
    });
  }

  findByPlayerAndSeason(player_id: string, season: string) {
    const games = this.gameRepository
      .createQueryBuilder('game')
      .leftJoinAndSelect('game.player', 'player')
      .where('player.player_id = :player_id', { player_id })
      .andWhere('player.season = :season', { season })
      .getMany();
    return games;
  }
}
