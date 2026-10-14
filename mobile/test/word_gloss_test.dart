import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mobile/api_service.dart';
import 'package:mobile/widgets/interactive_arabic_text.dart';

void main() {
  late List<Uri> requests;

  setUp(() {
    requests = [];
    WordGloss.api = ApiService(
      baseUrl: 'https://api.example.test',
      client: MockClient((request) async {
        requests.add(request.url);
        return http.Response(
          jsonEncode({'translation': 'a means', 'part_of_speech': 'noun', 'source': 'gemini'}),
          200,
          headers: {'content-type': 'application/json; charset=utf-8'},
        );
      }),
    );
  });

  test('unknown words no longer fall back to a placeholder', () {
    expect(lookupArabicWord('وَسِيلَةٌ'), isEmpty);
    expect(WordGloss.meaning('وَسِيلَةٌ', 'المال وسيلة'), WordGloss.loadingText);
  });

  test('fetches unknown words once with the passage as context', () async {
    const passage = 'لأنّ المال وسيلة لتحقيق الرغبات';
    expect(await WordGloss.ensure('وَسِيلَةٌ،', passage), 'a means');
    expect(await WordGloss.ensure('وَسِيلَةٌ،', passage), 'a means');
    expect(WordGloss.meaning('وَسِيلَةٌ،', passage), 'a means');
    expect(requests, hasLength(1));
    expect(requests.single.path, '/api/curriculum/word-gloss');
    expect(requests.single.queryParameters['word'], 'وَسِيلَةٌ');
    expect(requests.single.queryParameters['context'], passage);
  });

  test('dictionary words are answered locally', () async {
    expect(await WordGloss.ensure('ضمة', ''), isNot(WordGloss.unavailableText));
    expect(requests, isEmpty);
  });

  testWidgets('InteractiveArabicText renders with the gloss notifier', (tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: Scaffold(body: InteractiveArabicText(text: 'المال وسيلة')),
    ));
    expect(find.text('وسيلة'), findsOneWidget);
  });
}
