<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class AccessLog extends Model
{
    protected $table = 'access_logs';
    protected $primaryKey = 'id';
    public $timestamps = true;

    protected $fillable = ['datetime', 'method', 'success', 'user_id'];

    public function user()
    {
        return $this->belongsTo(User::class, 'user_id');
    }
}
