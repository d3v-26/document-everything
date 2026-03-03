import { query } from './lib/utils';

async function main() {
  const result = await query('SELECT 1');
  console.log(result);
}

main();
