// Older backends used the application name for the bundled OmniVoice model.
export function engineDisplayName(name = '') {
  return name.replace(/^VoiceBlueprint(?= \(k2-fsa\/OmniVoice| TTS$|$)/, 'OmniVoice');
}
