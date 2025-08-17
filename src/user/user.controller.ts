import { Body, Controller, Get, Param, Post } from '@nestjs/common';
import { CreateUserDto } from './dto/create-user.dto';
import { UserService } from './user.service';

@Controller('user')
export class UserController {
  constructor(private userService: UserService) {}

  @Post('single')
  create(@Body() createUserDto: CreateUserDto) {
    return this.userService.create(createUserDto);
  }

  @Post('bulk')
  createBulk(@Body() createUserDtos: CreateUserDto[]) {
    return this.userService.createBulk(createUserDtos);
  }

  @Get(':user_id')
  findOne(@Param('user_id') user_id: string) {
    return this.userService.findOne(user_id);
  }

  @Get()
  findAll() {
    return this.userService.findAll();
  }

  @Get(':user_id/players')
  findUserPlayers(@Param('user_id') user_id: string) {
    return this.userService.findUserPlayers(user_id);
  }
}
