import { Controller } from '@nestjs/common';
import { CreateUserDto } from './dto/create-user.dto';
import { UserService } from './user.service';

@Controller('user')
export class UserController {
  constructor(private userService: UserService) {}

  create(createUserDto: CreateUserDto) {
    return this.userService.create(createUserDto);
  }
}
