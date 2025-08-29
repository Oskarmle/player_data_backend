import { Controller, Get, Param } from '@nestjs/common';
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

  @Get('/:player_id/games')
  findPlayerGames(@Param('player_id') player_id: string) {
    return this.gameService.findPlayerGames(player_id);
  }

  @Get('/user/:user_id/games')
  findUserGames(@Param('user_id') user_id: string) {
    return this.gameService.findUserGames(user_id);
  }

  @Get('user/stats/:userId')
  gamesStatsUser(@Param('userId') userId: string) {
    return this.gameService.gamesStatsUser(userId);
  }

  @Get('player/stats/:playerId')
  gamesStatsPlayer(@Param('playerId') playerId: string) {
    return this.gameService.gamesStatsPlayer(playerId);
  }
}
