import { Injectable } from '@nestjs/common';
import { Repository } from 'typeorm';
import { User } from './entities/user.entity';
import { CreateUserDto } from './dto/create-user.dto';
import { InjectRepository } from '@nestjs/typeorm';

@Injectable()
export class UserService {
  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
  ) {}

  create(createUserDto: CreateUserDto) {
    const user = this.userRepository.create(createUserDto);
    return this.userRepository.save(user);
  }

  createBulk(createUserDtos: CreateUserDto[]) {
    const users = this.userRepository.create(createUserDtos);
    return this.userRepository.save(users);
  }

  findOne(user_id: string) {
    return this.userRepository.findOne({ where: { user_id: user_id } });
  }

  findUserPlayers(user_id: string) {
    return this.userRepository.findOne({
      where: { user_id: user_id },
      relations: ['players'],
    });
  }
}
