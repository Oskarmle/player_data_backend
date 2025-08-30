import { TypeOrmModuleOptions } from '@nestjs/typeorm';
import * as dotenv from 'dotenv';
import { Game } from 'src/game/entities/game.entity';
import { Player } from 'src/player/entities/player.entity';
import { DataSource, DataSourceOptions } from 'typeorm';
import { User } from './user/entities/user.entity';

dotenv.config();

export const dbConfig: TypeOrmModuleOptions = {
  type: 'postgres',
  url: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
  synchronize: false, // Setting synchronize: true shouldn't be used in production - otherwise you can lose production data.
  entities: [Player, Game, User],
  migrations: ['dist/src/migrations/*{.ts,.js}'],
};

const datasource = new DataSource(dbConfig as DataSourceOptions);
export default datasource;
