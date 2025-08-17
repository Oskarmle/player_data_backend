import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Player } from './entities/player.entity';
import { Repository } from 'typeorm';

@Injectable()
export class PlayerService {
  constructor(
    @InjectRepository(Player)
    private playerRepository: Repository<Player>,
  ) {}

  findAll() {
    return this.playerRepository.find();
  }

  findOne(player_id: string) {
    return this.playerRepository.findOneBy({ player_id: player_id });
  }

  findAllUserPlayers(user_id: string) {
    return this.playerRepository.find({
      where: { user: { user_id: user_id } },
    });
  }
}
