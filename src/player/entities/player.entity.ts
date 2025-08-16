import { Game } from 'src/game/entities/game.entity';
import { User } from 'src/user/entities/user.entity';
import {
  Column,
  Entity,
  JoinColumn,
  ManyToOne,
  OneToMany,
  PrimaryColumn,
} from 'typeorm';

@Entity('players')
export class Player {
  @PrimaryColumn()
  player_id: string;

  @Column()
  rank: number;

  @Column()
  season: string;

  @Column()
  player_link: string;

  @Column()
  player_club: string;

  @Column()
  current_points: number;

  @ManyToOne(() => User, (user) => user.players)
  @JoinColumn({ name: 'user_id' })
  user: User;

  @OneToMany(() => Game, (game) => game.player)
  games: Game[] | null;
}
