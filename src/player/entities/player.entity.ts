import { Game } from 'src/game/entities/game.entity';
import { Column, Entity, OneToMany, PrimaryColumn } from 'typeorm';

@Entity('players')
export class Player {
  @PrimaryColumn()
  player_id: string;

  @Column()
  rank: number;

  @Column()
  name: string;

  @Column()
  player_link: string;

  @Column()
  player_club: string;

  @Column()
  current_points: number;

  @OneToMany(() => Game, (game) => game.player)
  games: Game[] | null;
}
