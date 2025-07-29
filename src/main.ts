import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import datasource from 'data.source';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.enableCors({
    origin: 'http://localhost:3001',
  });

  await app.listen(process.env.PORT ?? 3000);
  try {
    await datasource.initialize();
    console.log('✅ DB Connection successful!');
  } catch (err) {
    console.error('❌ DB Connection failed:', err);
  }
}
void bootstrap();
