/**
 * Mocks globais dos módulos nativos usados pelo app SIGIL. Sem eles,
 * qualquer teste que importe hashService/authService/panicoService
 * falharia ao tentar acessar APIs nativas inexistentes no ambiente
 * de teste (Node.js, sem runtime iOS/Android real).
 */

jest.mock('react-native-keychain', () => ({
  setGenericPassword: jest.fn(() => Promise.resolve(true)),
  getGenericPassword: jest.fn(() => Promise.resolve(false)),
  resetGenericPassword: jest.fn(() => Promise.resolve(true)),
  ACCESSIBLE: { WHEN_UNLOCKED_THIS_DEVICE_ONLY: 'AccessibleWhenUnlockedThisDeviceOnly' },
}));

jest.mock('react-native-fs', () => ({
  readFile: jest.fn(() => Promise.resolve('base64-mock-content')),
  exists: jest.fn(() => Promise.resolve(false)),
  unlink: jest.fn(() => Promise.resolve()),
  CachesDirectoryPath: '/mock/caches',
  DocumentDirectoryPath: '/mock/documents',
}));

jest.mock('react-native-crypto', () => ({
  sha256: jest.fn((buffer) => ({
    toString: () => 'mocked-sha256-hash-' + String(buffer).length,
  })),
  createHmac: jest.fn(() => ({
    update: jest.fn().mockReturnThis(),
    digest: jest.fn(() => 'mocked-hmac-signature'),
  })),
  randomBytes: jest.fn((size) => ({
    toString: () => 'mocked-random-' + size,
  })),
}));

jest.mock('react-native-biometrics', () => {
  return jest.fn().mockImplementation(() => ({
    isSensorAvailable: jest.fn(() =>
      Promise.resolve({ available: true, biometryType: 'Biometrics' })
    ),
    simplePrompt: jest.fn(() => Promise.resolve({ success: true })),
    createKeys: jest.fn(() => Promise.resolve({ publicKey: 'mock-public-key' })),
    createSignature: jest.fn(() =>
      Promise.resolve({ success: true, signature: 'mock-signature' })
    ),
  }));
});

jest.mock('react-native-geolocation-service', () => ({
  getCurrentPosition: jest.fn((onSuccess) =>
    onSuccess({ coords: { latitude: -3.7327, longitude: -38.5267 } })
  ),
}));

jest.mock('react-native-sqlcipher-storage', () => ({
  DEBUG: jest.fn(),
  enablePromise: jest.fn(),
  openDatabase: jest.fn(() =>
    Promise.resolve({
      executeSql: jest.fn(() => Promise.resolve([{ rows: { length: 0, item: () => null } }])),
    })
  ),
}));

jest.mock('react-native-image-crop-picker', () => ({
  openCamera: jest.fn(() =>
    Promise.resolve({
      path: '/mock/foto.jpg',
      mime: 'image/jpeg',
      size: 12345,
      width: 1600,
      height: 1200,
    })
  ),
}));

jest.mock('react-native-audio-recorder-player', () => {
  return jest.fn().mockImplementation(() => ({
    startRecorder: jest.fn(() => Promise.resolve('/mock/audio.m4a')),
    stopRecorder: jest.fn(() => Promise.resolve('/mock/audio.m4a')),
    addRecordBackListener: jest.fn(),
    removeRecordBackListener: jest.fn(),
  }));
});

jest.mock('axios');
