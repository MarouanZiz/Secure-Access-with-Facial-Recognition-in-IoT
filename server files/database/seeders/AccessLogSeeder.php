<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use App\Models\AccessLog;


class AccessLogSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Seed data for access_logs table
        AccessLog::create([
            'datetime' => '2023-07-01 10:00:00',
            'method' => 'GET',
            'success' => true,
            'user_id' => 1,
            'image_path' => null,
        ]);

        AccessLog::create([
            'datetime' => '2023-07-02 15:30:00',
            'method' => 'POST',
            'success' => false,
            'user_id' => 2,
            'image_path' => 'path/to/image.jpg',
        ]);
    }
}
