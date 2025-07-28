import { Player } from 'src/player/entities/player.entity';
import { Column, Entity, JoinColumn, ManyToOne, PrimaryColumn } from 'typeorm';

@Entity('games')
export class Game {
  @PrimaryColumn()
  game_id: string;

  @Column()
  game_date: Date;

  @Column()
  opponent_name: string;

  @Column()
  opponent_link: string;

  @Column()
  opponent_rating: number;

  @Column()
  opponent_club: string;

  @Column()
  player_rating: number;

  @Column()
  gained_lost: number;

  @Column()
  tournament: string;

  @ManyToOne(() => Player, (player) => player.games)
  @JoinColumn({ name: 'player_id' })
  player: Player;
}
