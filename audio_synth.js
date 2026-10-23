class SonoraAudioEngine {
  constructor() {
    this.audioCtx = null;
    this.isPlaying = false;
    this.currentSong = null;
    this.elapsedSeconds = 0;
    this.durationSeconds = 180;
    this.volume = 0.8;
    this.timerInterval = null;
    this.synthLoopInterval = null;
    this.onProgressCallback = null;
    this.onEndCallback = null;
    this.analyser = null;
    this.masterGain = null;
    this.customAudio = null;
  }

  init() {
    if (!this.audioCtx) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      this.audioCtx = new AudioContextClass();
      this.masterGain = this.audioCtx.createGain();
      this.masterGain.gain.setValueAtTime(this.volume, this.audioCtx.currentTime);

      this.analyser = this.audioCtx.createAnalyser();
      this.analyser.fftSize = 64;

      this.masterGain.connect(this.analyser);
      this.analyser.connect(this.audioCtx.destination);
    }

    if (this.audioCtx.state === 'suspended') {
      this.audioCtx.resume();
    }
  }

  setVolume(val) {
    this.volume = Math.max(0, Math.min(1, val));
    if (this.masterGain && this.audioCtx) {
      this.masterGain.gain.setValueAtTime(this.volume, this.audioCtx.currentTime);
    }
    if (this.customAudio) {
      this.customAudio.volume = this.volume;
    }
  }

  playSong(song, startSeconds = 0) {
    this.init();
    this.stop();

    this.currentSong = song;
    this.durationSeconds = song.duration || 180;
    this.elapsedSeconds = startSeconds;
    this.isPlaying = true;

    if (song.audio_url && song.audio_url.startsWith('http')) {
      this.customAudio = new Audio(song.audio_url);
      this.customAudio.currentTime = startSeconds;
      this.customAudio.volume = this.volume;
      this.customAudio.play().catch(e => {
        console.warn('Custom audio playback failed, falling back to Web Audio Synth', e);
        this.startProceduralSynth(song);
      });
      this.customAudio.onended = () => {
        if (this.onEndCallback) this.onEndCallback();
      };
    } else {
      this.startProceduralSynth(song);
    }

    this.timerInterval = setInterval(() => {
      this.elapsedSeconds += 1;
      if (this.onProgressCallback) {
        this.onProgressCallback(this.elapsedSeconds, this.durationSeconds);
      }
      if (this.elapsedSeconds >= this.durationSeconds) {
        this.stop();
        if (this.onEndCallback) {
          this.onEndCallback();
        }
      }
    }, 1000);
  }

  startProceduralSynth(song) {
    const genre = (song.genre || '').toLowerCase();
    
    let chordFreqs;
    let waveType = 'sine';

    if (genre.includes('synth') || genre.includes('electronic')) {
      chordFreqs = [220, 277.18, 329.63, 440]; 
      waveType = 'sawtooth';
    } else if (genre.includes('jazz') || genre.includes('blues')) {
      chordFreqs = [196, 246.94, 293.66, 349.23]; 
      waveType = 'triangle';
    } else if (genre.includes('lo-fi') || genre.includes('chill')) {
      chordFreqs = [261.63, 329.63, 392.00, 493.88]; 
      waveType = 'sine';
    } else if (genre.includes('acoustic') || genre.includes('folk')) {
      chordFreqs = [146.83, 220, 293.66, 369.99]; 
      waveType = 'triangle';
    } else {
      chordFreqs = [220, 261.63, 329.63, 392.00]; 
      waveType = 'sine';
    }

    let noteIndex = 0;
    const playNote = () => {
      if (!this.isPlaying || !this.audioCtx) return;

      const osc = this.audioCtx.createOscillator();
      const noteGain = this.audioCtx.createGain();

      const freq = chordFreqs[noteIndex % chordFreqs.length];
      osc.type = waveType;
      osc.frequency.setValueAtTime(freq, this.audioCtx.currentTime);

      const filter = this.audioCtx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(950, this.audioCtx.currentTime);

      noteGain.gain.setValueAtTime(0.01, this.audioCtx.currentTime);
      noteGain.gain.exponentialRampToValueAtTime(0.2, this.audioCtx.currentTime + 0.1);
      noteGain.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + 1.8);

      osc.connect(filter);
      filter.connect(noteGain);
      noteGain.connect(this.masterGain);

      osc.start();
      osc.stop(this.audioCtx.currentTime + 1.9);

      noteIndex = (noteIndex + 1) % chordFreqs.length;
    };

    playNote();
    this.synthLoopInterval = setInterval(playNote, 900);
  }

  pause() {
    this.isPlaying = false;
    if (this.synthLoopInterval) {
      clearInterval(this.synthLoopInterval);
      this.synthLoopInterval = null;
    }
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
    if (this.customAudio) {
      this.customAudio.pause();
    }
  }

  resume() {
    if (this.currentSong) {
      this.playSong(this.currentSong, this.elapsedSeconds);
    }
  }

  stop() {
    this.isPlaying = false;
    if (this.synthLoopInterval) {
      clearInterval(this.synthLoopInterval);
      this.synthLoopInterval = null;
    }
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
    if (this.customAudio) {
      this.customAudio.pause();
      this.customAudio = null;
    }
  }

  seek(seconds) {
    this.elapsedSeconds = Math.max(0, Math.min(this.durationSeconds, seconds));
    if (this.customAudio) {
      this.customAudio.currentTime = this.elapsedSeconds;
    }
    if (this.isPlaying) {
      this.resume();
    }
  }
}

window.sonoraAudio = new SonoraAudioEngine();

