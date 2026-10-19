import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:mobile/api_service.dart';
import 'package:mobile/widgets/aligned_sentence.dart';

const _ar = 'الحِصَانُ سَرِيعٌ.';
const _en = 'The horse is fast.';
const _chunks = [
  {'ar': [0], 'en': [0, 1]},
  {'ar': [1], 'en': [3]},
];

void main() {
  test('AlignmentChunk.listFromJson accepts chunks and rejects malformed data', () {
    final chunks = AlignmentChunk.listFromJson(_chunks)!;
    expect(chunks.first.en, [0, 1]);
    expect(AlignmentChunk.listFromJson(null), isNull);
    expect(AlignmentChunk.listFromJson([]), isNull);
    expect(AlignmentChunk.listFromJson([{'ar': [], 'en': [1]}]), isNull);
  });

  test('AlignmentStore fetches each pair once and keeps the answers', () async {
    var calls = 0;
    final api = ApiService(
      baseUrl: 'http://test',
      client: MockClient((request) async {
        calls++;
        final pairs = (jsonDecode(request.body) as Map)['pairs'] as List;
        expect(request.url.path, '/api/curriculum/alignments');
        return http.Response(
          jsonEncode({'alignments': [for (final p in pairs) p['ar'] == _ar ? _chunks : null]}),
          200,
          headers: {'content-type': 'application/json'},
        );
      }),
    );
    final pairs = [const MapEntry(_ar, _en), const MapEntry('مرحبا', 'Hello')];
    expect(await AlignmentStore.request(api, pairs), isTrue);
    expect(await AlignmentStore.request(api, pairs), isFalse);
    expect(calls, 1);
    expect(AlignmentStore.lookup(_ar, _en)!.length, 2);
    expect(AlignmentStore.lookup('مرحبا', 'Hello'), isNull);
  });

  testWidgets('tapping a word highlights its match on the other side', (tester) async {
    final spoken = <String>[];
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: AlignedSentenceView(
          ar: _ar,
          en: _en,
          chunks: AlignmentChunk.listFromJson(_chunks)!,
          onVocalize: spoken.add,
        ),
      ),
    ));
    Color? background(String text) {
      final container = tester.widget<Container>(
        find.ancestor(of: find.text(text), matching: find.byType(Container)).first,
      );
      return (container.decoration as BoxDecoration).color;
    }

    expect(background('horse'), Colors.transparent);
    await tester.tap(find.text('الحِصَانُ'));
    await tester.pump();
    expect(spoken, ['الحِصَانُ']);
    expect(background('The'), isNot(Colors.transparent));
    expect(background('horse'), isNot(Colors.transparent));
    expect(background('fast.'), Colors.transparent);

    await tester.tap(find.text('fast.'));
    await tester.pump();
    expect(background('سَرِيعٌ.'), isNot(Colors.transparent));
    expect(background('horse'), Colors.transparent);
  });
}
