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

  @Get(':player_id/games')
  findPlayerGames(@Param('player_id') player_id: string) {
    return this.playerService.findPlayerGames(player_id);
  }
}
