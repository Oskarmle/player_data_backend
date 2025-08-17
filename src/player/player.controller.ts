import { Controller, Get, Param } from '@nestjs/common';
import { PlayerService } from './player.service';

@Controller('player')
export class PlayerController {
  constructor(private playerService: PlayerService) {}

  @Get()
  findAll() {
    return this.playerService.findAll();
  }

  @Get(':player_id')
  findOne(@Param('player_id') player_id: string) {
    return this.playerService.findOne(player_id);
  }

  @Get(':user_id/players')
  findAllUserPlayers(@Param('user_id') user_id: string) {
    return this.playerService.findAllUserPlayers(user_id);
  }
}
