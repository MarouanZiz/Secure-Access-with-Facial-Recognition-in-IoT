<?php

namespace App\Http\Controllers;

use App\Models\AccessLog;
use Illuminate\Http\Request;

class AccessLogController extends Controller
{
    public function index()
    {
        $accessLogs = AccessLog::all();
        return response()->json($accessLogs);
    }

    public function show($id)
    {
        $accessLog = AccessLog::find($id);
        if (!$accessLog) {
            return response()->json(['message' => 'Access log not found'], 404);
        }
        return response()->json($accessLog);
    }

    public function store(Request $request)
    {
        $this->validate($request, [
            'datetime' => 'required|date',
            'method' => 'required|string|max:50',
            'success' => 'required|boolean',
            'user_id' => 'required|integer',
            'image_path' => 'nullable|string',
        ]);

        $accessLog = AccessLog::create($request->all());
        return response()->json($accessLog, 201);
    }

    public function update(Request $request, $id)
    {
        $accessLog = AccessLog::find($id);
        if (!$accessLog) {
            return response()->json(['message' => 'Access log not found'], 404);
        }

        $this->validate($request, [
            'datetime' => 'required|date',
            'method' => 'required|string|max:50',
            'success' => 'required|boolean',
            'user_id' => 'required|integer',
            'image_path' => 'nullable|string',
        ]);

        $accessLog->update($request->all());
        return response()->json($accessLog);
    }

    public function destroy($id)
    {
        $accessLog = AccessLog::find($id);
        if (!$accessLog) {
            return response()->json(['message' => 'Access log not found'], 404);
        }

        $accessLog->delete();
        return response()->json(['message' => 'Access log deleted']);
    }
}
