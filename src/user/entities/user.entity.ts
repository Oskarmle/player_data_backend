import { Player } from 'src/player/entities/player.entity';
import { Column, Entity, OneToMany, PrimaryGeneratedColumn } from 'typeorm';

@Entity('users')
export class User {
  @PrimaryGeneratedColumn('uuid')
  user_id: string;

  @Column()
  name: string;

  @OneToMany(() => Player, (player) => player.user)
  players?: Player[];
}
