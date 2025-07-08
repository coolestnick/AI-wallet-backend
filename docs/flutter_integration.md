# Flutter Integration Guide for Salt Wallet

## Overview

This guide outlines how to integrate the Salt Wallet API with a Flutter mobile application. The Flutter app will provide users with access to our three specialized AI agents: Crypto Advisor, Market Research, and Portfolio Management.

## Setup Requirements

- Flutter SDK 3.10.0 or higher
- Dart 3.0.0 or higher
- [http](https://pub.dev/packages/http) package for API calls
- [provider](https://pub.dev/packages/provider) or [riverpod](https://pub.dev/packages/riverpod) for state management
- [flutter_dotenv](https://pub.dev/packages/flutter_dotenv) for environment variables

## Project Configuration

Add the required dependencies to your `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  provider: ^6.0.5  # Or riverpod: ^2.3.6
  flutter_dotenv: ^5.1.0
  flutter_markdown: ^0.6.17  # For rendering markdown responses
  shared_preferences: ^2.2.0  # For storing user data

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^2.0.0
```

Create a `.env` file in your project root:

```
API_BASE_URL=https://your-api-url.com  # For production
# API_BASE_URL=http://localhost:8000    # For local development
```

## API Service Implementation

Create a service class to interact with the Salt Wallet API:

```dart
// lib/services/agent_service.dart
import 'dart:convert';
import 'dart:async';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;

class AgentService {
  final String baseUrl = dotenv.env['API_BASE_URL'] ?? 'http://localhost:8000';
  final String apiPrefix = '/api/v1';
  
  // Get list of available agents
  Future<List<dynamic>> getAgents() async {
    final response = await http.get(
      Uri.parse('$baseUrl$apiPrefix/agents'),
      headers: {'Content-Type': 'application/json'},
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to load agents');
    }
  }
  
  // Chat with an agent
  Future<Map<String, dynamic>> chatWithAgent({
    required String agentId, 
    required String message,
    required String userId,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl$apiPrefix/agents/$agentId/chat'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'messages': [{'role': 'user', 'content': message}],
        'agent_id': agentId,
        'user_id': userId,
      }),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to send message');
    }
  }
  
  // Stream chat with an agent (for real-time responses)
  Stream<String> streamChatWithAgent({
    required String agentId,
    required String message,
    required String userId,
  }) async* {
    // For now, while the backend streaming is not implemented, 
    // use our mockStreamChatWithAgent instead
    yield* mockStreamChatWithAgent(
      agentId: agentId,
      message: message,
      userId: userId,
    );
  }
  
  // Mock streaming implementation to showcase the feature
  Stream<String> mockStreamChatWithAgent({
    required String agentId,
    required String message,
    required String userId,
  }) async* {
    // First yield a loading message
    yield "Loading response...";
    
    // Wait a moment to simulate network request
    await Future.delayed(const Duration(milliseconds: 500));
    
    try {
      // Get the full response from the regular chat endpoint
      final response = await chatWithAgent(
        agentId: agentId,
        message: message,
        userId: userId,
      );
      
      // Get the full content
      final fullContent = response['message']['content'] as String;
      
      // Split the content into words to simulate streaming
      final words = fullContent.split(' ');
      
      // Buffer to build up the streamed response
      String buffer = '';
      
      // Stream the words with small delays to simulate typing
      for (final word in words) {
        buffer += (buffer.isEmpty ? '' : ' ') + word;
        yield buffer;
        
        // Random delay between 50-150ms to simulate realistic typing
        await Future.delayed(Duration(milliseconds: 50 + (100 * word.length / 10).round()));
      }
    } catch (e) {
      yield "Sorry, I encountered an error while processing your request: $e";
    }
  }
}
```

## State Management

Here's an example of a simple provider-based state management approach for your chat screen:

```dart
// lib/providers/chat_provider.dart
import 'package:flutter/foundation.dart';
import '../services/agent_service.dart';

class Message {
  final String id;
  final String content;
  final String timestamp;
  final bool isUser;
  
  Message({
    required this.id,
    required this.content,
    required this.timestamp,
    required this.isUser,
  });
}

class ChatProvider extends ChangeNotifier {
  final AgentService _agentService = AgentService();
  final List<Message> _messages = [];
  bool _isLoading = false;
  String _errorMessage = '';
  
  List<Message> get messages => [..._messages];
  bool get isLoading => _isLoading;
  String get errorMessage => _errorMessage;
  
  Future<void> sendMessage({
    required String agentId,
    required String content,
    required String userId,
  }) async {
    _isLoading = true;
    _errorMessage = '';
    notifyListeners();
    
    // Add user message to chat
    _messages.add(Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: content,
      timestamp: DateTime.now().toIso8601String(),
      isUser: true,
    ));
    notifyListeners();
    
    try {
      final response = await _agentService.chatWithAgent(
        agentId: agentId,
        message: content,
        userId: userId,
      );
      
      // Add agent response to chat
      _messages.add(Message(
        id: response['message_id'] ?? DateTime.now().millisecondsSinceEpoch.toString(),
        content: response['message']['content'] ?? "No response content",
        timestamp: DateTime.now().toIso8601String(),
        isUser: false,
      ));
    } catch (e) {
      _errorMessage = 'Failed to get response: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  void clearChat() {
    _messages.clear();
    _errorMessage = '';
    notifyListeners();
  }
}
```

## UI Implementation

### Agent Selection Screen

```dart
// lib/screens/agent_selection_screen.dart
import 'package:flutter/material.dart';
import '../services/agent_service.dart';

class AgentSelectionScreen extends StatefulWidget {
  const AgentSelectionScreen({Key? key}) : super(key: key);

  @override
  State<AgentSelectionScreen> createState() => _AgentSelectionScreenState();
}

class _AgentSelectionScreenState extends State<AgentSelectionScreen> {
  final AgentService _agentService = AgentService();
  late Future<List<dynamic>> _agentsFuture;
  
  @override
  void initState() {
    super.initState();
    _agentsFuture = _agentService.getAgents();
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Salt Wallet'),
      ),
      body: FutureBuilder<List<dynamic>>(
        future: _agentsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('No agents available'));
          }
          
          return ListView.builder(
            itemCount: snapshot.data!.length,
            itemBuilder: (context, index) {
              final agent = snapshot.data![index];
              return AgentCard(
                id: agent['id'],
                name: agent['name'],
                description: agent['description'],
                onTap: () {
                  Navigator.pushNamed(
                    context, 
                    '/chat',
                    arguments: {
                      'agentId': agent['id'],
                      'agentName': agent['name'],
                    },
                  );
                },
              );
            },
          );
        },
      ),
    );
  }
}

class AgentCard extends StatelessWidget {
  final String id;
  final String name;
  final String description;
  final VoidCallback onTap;
  
  const AgentCard({
    Key? key,
    required this.id,
    required this.name,
    required this.description,
    required this.onTap,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                name,
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 8),
              Text(description),
              const SizedBox(height: 16),
              Align(
                alignment: Alignment.centerRight,
                child: ElevatedButton(
                  onPressed: onTap,
                  child: const Text('Chat Now'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

### Chat Screen

```dart
// lib/screens/chat_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/chat_provider.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

class ChatScreen extends StatefulWidget {
  final String agentId;
  final String agentName;
  
  const ChatScreen({
    Key? key,
    required this.agentId,
    required this.agentName,
  }) : super(key: key);
  
  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final String _userId = 'user_123'; // Should be retrieved from auth service
  
  @override
  void dispose() {
    _messageController.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.agentName),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete),
            onPressed: () {
              Provider.of<ChatProvider>(context, listen: false).clearChat();
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: Consumer<ChatProvider>(
              builder: (context, chatProvider, child) {
                final messages = chatProvider.messages;
                
                if (messages.isEmpty) {
                  return Center(
                    child: Text(
                      'Start chatting with ${widget.agentName}',
                      style: Theme.of(context).textTheme.bodyLarge,
                    ),
                  );
                }
                
                return ListView.builder(
                  reverse: true,
                  itemCount: messages.length,
                  itemBuilder: (context, index) {
                    final message = messages[messages.length - 1 - index];
                    return MessageBubble(
                      content: message.content,
                      isUser: message.isUser,
                    );
                  },
                );
              },
            ),
          ),
          Consumer<ChatProvider>(
            builder: (context, chatProvider, child) {
              if (chatProvider.isLoading) {
                return const Padding(
                  padding: EdgeInsets.all(8.0),
                  child: LinearProgressIndicator(),
                );
              }
              return const SizedBox.shrink();
            },
          ),
          if (context.watch<ChatProvider>().errorMessage.isNotEmpty)
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Text(
                context.watch<ChatProvider>().errorMessage,
                style: const TextStyle(color: Colors.red),
              ),
            ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: const InputDecoration(
                      hintText: 'Type your message...',
                      border: OutlineInputBorder(),
                    ),
                    minLines: 1,
                    maxLines: 5,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.send),
                  onPressed: () {
                    final message = _messageController.text.trim();
                    if (message.isNotEmpty) {
                      Provider.of<ChatProvider>(context, listen: false).sendMessage(
                        agentId: widget.agentId,
                        content: message,
                        userId: _userId,
                      );
                      _messageController.clear();
                    }
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class MessageBubble extends StatelessWidget {
  final String content;
  final bool isUser;
  
  const MessageBubble({
    Key? key,
    required this.content,
    required this.isUser,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isUser 
              ? Theme.of(context).colorScheme.primary
              : Theme.of(context).colorScheme.secondary.withOpacity(0.3),
          borderRadius: BorderRadius.circular(12),
        ),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        child: isUser
            ? Text(
                content,
                style: TextStyle(
                  color: isUser ? Colors.white : Colors.black,
                ),
              )
            : MarkdownBody(
                data: content,
                styleSheet: MarkdownStyleSheet(
                  p: const TextStyle(fontSize: 16),
                  code: const TextStyle(
                    backgroundColor: Colors.black12,
                    fontFamily: 'monospace',
                  ),
                ),
              ),
      ),
    );
  }
}
```

## Theme Implementation

Create a custom theme for your app with dark mode support:

```dart
// lib/theme/app_theme.dart
import 'package:flutter/material.dart';

class AppTheme {
  static ThemeData lightTheme() {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: Colors.indigo,
        brightness: Brightness.light,
      ),
      appBarTheme: const AppBarTheme(
        centerTitle: true,
        elevation: 0,
      ),
      cardTheme: CardTheme(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    );
  }

  static ThemeData darkTheme() {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: Colors.indigo,
        brightness: Brightness.dark,
      ),
      appBarTheme: const AppBarTheme(
        centerTitle: true,
        elevation: 0,
      ),
      cardTheme: CardTheme(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    );
  }
}
```

## Main App

Configure the main app with providers and routes:

```dart
// lib/main.dart
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:provider/provider.dart';
import 'providers/chat_provider.dart';
import 'screens/agent_selection_screen.dart';
import 'screens/chat_screen.dart';
import 'theme/app_theme.dart';

Future<void> main() async {
  await dotenv.load(fileName: '.env');
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ChatProvider()),
      ],
      child: MaterialApp(
        title: 'Salt Wallet',
        theme: AppTheme.lightTheme(),
        darkTheme: AppTheme.darkTheme(),
        themeMode: ThemeMode.system,
        initialRoute: '/',
        routes: {
          '/': (context) => const AgentSelectionScreen(),
        },
        onGenerateRoute: (settings) {
          if (settings.name == '/chat') {
            final args = settings.arguments as Map<String, dynamic>;
            return MaterialPageRoute(
              builder: (context) => ChatScreen(
                agentId: args['agentId'],
                agentName: args['agentName'],
              ),
            );
          }
          return null;
        },
      ),
    );
  }
}
```

## Best Practices

1. **Error Handling**: Always handle API errors gracefully and display friendly error messages to the user.

2. **Loading States**: Show loading indicators during API calls to provide feedback to the user.

3. **Caching**: Consider implementing caching for agent responses to reduce API calls and improve performance.

4. **Authentication**: Implement proper authentication if the API requires it. You can use packages like `flutter_secure_storage` to store tokens securely.

5. **Connectivity**: Check for internet connectivity before making API calls and provide appropriate feedback if the device is offline.

6. **Responsiveness**: Design your UI to work well on both phones and tablets.

7. **Localization**: Consider implementing localization for supporting multiple languages.

## Streaming Implementation (Advanced)

For a better user experience with streaming responses, consider this alternative implementation for the chat screen:

```dart
// Alternative implementation for streaming responses
Stream<String> streamResponse({
  required String agentId,
  required String message,
  required String userId,
}) {
  final controller = StreamController<String>();
  
  _agentService.streamChatWithAgent(
    agentId: agentId,
    message: message,
    userId: userId,
  ).listen(
    (chunk) {
      controller.add(chunk);
    },
    onDone: () {
      controller.close();
    },
    onError: (error) {
      controller.addError(error);
      controller.close();
    },
  );
  
  return controller.stream;
}
```

## Testing

Create unit tests for your services and widget tests for your UI components:

```dart
// test/agent_service_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:your_app/services/agent_service.dart';
import 'dart:convert';

void main() {
  group('AgentService', () {
    late AgentService agentService;
    
    setUp(() {
      agentService = AgentService();
    });
    
    test('getAgents returns a list of agents on success', () async {
      // Mock implementation
      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode([
            {
              'id': 'crypto-advisor',
              'name': 'Crypto Advisor',
              'description': 'Expert guidance on cryptocurrency investments',
            },
          ]),
          200,
        );
      });
      
      // Test implementation
      final result = await agentService.getAgents();
      
      expect(result, isA<List>());
      expect(result.length, 1);
      expect(result[0]['id'], 'crypto-advisor');
    });
    
    // Add more tests for other methods
  });
}
```

## Conclusion

This integration guide provides a comprehensive foundation for building a Flutter mobile app that interacts with the Salt Wallet API. Follow these patterns and best practices to create a responsive, user-friendly application that leverages the full capabilities of our AI agents.

For additional support or questions, please contact our development team or refer to the API documentation. 