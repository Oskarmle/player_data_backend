import { TypeOrmModuleOptions } from '@nestjs/typeorm';
import * as dotenv from 'dotenv';
import { Game } from 'src/game/entities/game.entity';
import { Player } from 'src/player/entities/player.entity';
import { DataSource, DataSourceOptions } from 'typeorm';

dotenv.config();

export const dbConfig: TypeOrmModuleOptions = {
  type: 'postgres',
  url: process.env.DATABASE_URL_DEV,
  //   host: process.env.DB_HOST,
  //   port: parseInt(process.env.DB_PORT || '5432', 10),
  //   username: process.env.DB_USER,
  //   password: process.env.DB_PASSWORD,
  //   database: process.env.DB_NAME,
  ssl: { rejectUnauthorized: false },
  synchronize: true, // Setting synchronize: true shouldn't be used in production - otherwise you can lose production data.
  //   dropSchema: true, // This is useful for development to reset the database schema.
  entities: [Player, Game], // This makes the e2e test work
  migrations: ['dist/src/migrations/*{.ts,.js}'],
};

const datasource = new DataSource(dbConfig as DataSourceOptions);
export default datasource;
