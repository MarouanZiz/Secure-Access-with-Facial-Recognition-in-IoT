<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use App\Models\User;

class UserSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Seed data for users table
        User::create([
            'name' => 'John Doe',
            'face_image' => 'path/to/face_image.jpg',
            'rfid_code' => 'RFID123',
            'pin_code' => '1234'
        ]);

        User::create([
            'name' => 'Jane Smith',
            'face_image' => 'path/to/face_image.jpg',
            'rfid_code' => 'RFID456',
            'pin_code' => '5678'
        ]);
    }
}
