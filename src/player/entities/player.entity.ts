import { Game } from 'src/game/entities/game.entity';
import { Column, Entity, OneToMany, PrimaryColumn } from 'typeorm';

@Entity('players')
export class Player {
  @PrimaryColumn()
  player_id: string;

  @Column()
  player_link: string;

  @Column()
  firstName: string;

  @Column()
  lastName: string;

  @Column()
  team: string;

  @Column()
  season: string;

  @OneToMany(() => Game, (game) => game.player)
  games: Game[] | null;
}
