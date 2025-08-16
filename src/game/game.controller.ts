import { Controller, Get, Param, Query } from '@nestjs/common';
import { GameService } from './game.service';

@Controller('game')
export class GameController {
  constructor(private readonly gameService: GameService) {}

  @Get()
  findAll() {
    return this.gameService.findAll();
  }

  @Get(':game_id')
  findOne(game_id: string) {
    return this.gameService.findOne(game_id);
  }

  // @Get('player/:player_id')
  // findByPlayerId(@Param('player_id') player_id: string) {
  //   return this.gameService.findByPlayerId(player_id);
  // }

  @Get('player/:player_id')
  findByPlayerAndSeason(
    @Param('player_id') player_id: string,
    @Query('season') season: string,
  ) {
    return this.gameService.findByPlayerAndSeason(player_id, season);
  }
}
