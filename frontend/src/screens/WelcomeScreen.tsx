import React, { useEffect, useState, useRef } from 'react';
import { View, Text, StyleSheet, Animated, useWindowDimensions } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTheme } from '../theme/ThemeContext';
import { Button } from '../components/Button';

const CYCLE_WORDS = ['obsession.', 'adventure.', 'escape.', 'chapter.'];

export default function WelcomeScreen({ navigation }: any) {
  const { theme, spacing } = useTheme();
  const { width } = useWindowDimensions();

  const isWebOrTablet = width > 768;
  const headlineFontSize = isWebOrTablet ? 48 : 36;
  const headlineLineHeight = isWebOrTablet ? 58 : 46;

  const [wordIndex, setWordIndex] = useState(0);
  const [displayedWord, setDisplayedWord] = useState('');
  const [cursorVisible, setCursorVisible] = useState(true);
  const [phase, setPhase] = useState<'typing' | 'pausing' | 'deleting'>('typing');

  const logoOpacity = useRef(new Animated.Value(0)).current;
  const logoY = useRef(new Animated.Value(-8)).current;
  const headlineOpacity = useRef(new Animated.Value(0)).current;
  const headlineY = useRef(new Animated.Value(12)).current;
  const btnOpacity = useRef(new Animated.Value(0)).current;
  const btnY = useRef(new Animated.Value(18)).current;

  useEffect(() => {
    Animated.stagger(100, [
      Animated.parallel([
        Animated.timing(logoOpacity, { toValue: 1, duration: 300, useNativeDriver: true }),
        Animated.timing(logoY, { toValue: 0, duration: 300, useNativeDriver: true }),
      ]),
      Animated.parallel([
        Animated.timing(headlineOpacity, { toValue: 1, duration: 350, useNativeDriver: true }),
        Animated.timing(headlineY, { toValue: 0, duration: 350, useNativeDriver: true }),
      ]),
      Animated.parallel([
        Animated.timing(btnOpacity, { toValue: 1, duration: 350, useNativeDriver: true }),
        Animated.timing(btnY, { toValue: 0, duration: 350, useNativeDriver: true }),
      ]),
    ]).start();
  }, []);

  useEffect(() => {
    const current = CYCLE_WORDS[wordIndex];
    let timeout: ReturnType<typeof setTimeout>;

    if (phase === 'typing') {
      if (displayedWord.length < current.length) {
        timeout = setTimeout(() => {
          setDisplayedWord(current.slice(0, displayedWord.length + 1));
        }, 28);
      } else {
        timeout = setTimeout(() => setPhase('pausing'), 40);
      }
    }

    if (phase === 'pausing') {
      timeout = setTimeout(() => setPhase('deleting'), 1200);
    }

    if (phase === 'deleting') {
      if (displayedWord.length > 0) {
        timeout = setTimeout(() => {
          setDisplayedWord(displayedWord.slice(0, -1));
        }, 16);
      } else {
        setWordIndex((i) => (i + 1) % CYCLE_WORDS.length);
        setPhase('typing');
      }
    }

    return () => clearTimeout(timeout);
  }, [displayedWord, phase, wordIndex]);

  useEffect(() => {
    const blink = setInterval(() => {
      setCursorVisible((v) => !v);
    }, 480);
    return () => clearInterval(blink);
  }, []);

  const headlineStyle = {
    fontSize: headlineFontSize,
    lineHeight: headlineLineHeight,
    fontWeight: '800' as const,
    letterSpacing: -1,
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.background.primary }]}>
      <View style={styles.centerWrapper}>

        {/* TOP BAR — Left Aligned Logo */}
        <Animated.View
          style={[
            styles.topBrand,
            { opacity: logoOpacity, transform: [{ translateY: logoY }] },
          ]}
        >
          <Text style={[styles.brandText, { color: theme.brand.primary }]}>
            KITABEE
          </Text>
        </Animated.View>

        {/* HERO SECTION */}
        <View style={styles.hero}>
          <Animated.View
            style={{
              opacity: headlineOpacity,
              transform: [{ translateY: headlineY }],
              alignItems: 'flex-start',
              width: '100%',
            }}
          >
            <Text style={[headlineStyle, { color: theme.text.primary || '#F5F5F7' }]}>
              Your shelf, Their stories.
            </Text>

            <Text style={[headlineStyle, { color: theme.text.primary || '#F5F5F7' }]}>
              Find your next
            </Text>

            <View style={styles.line3Container}>
              <Text style={[headlineStyle, { color: theme.brand.primary }]}>
                {displayedWord}
                <Text
                  style={{
                    color: cursorVisible ? theme.brand.primary : 'transparent',
                    fontWeight: '300',
                  }}
                >
                  |
                </Text>
              </Text>
            </View>
          </Animated.View>
        </View>

        {/* ACTION BUTTONS */}
        <Animated.View
          style={[
            styles.actions,
            {
              opacity: btnOpacity,
              transform: [{ translateY: btnY }],
            },
          ]}
        >
          <Button
            title="SIGN UP FREE"
            onPress={() => navigation.navigate('Register')}
            style={{ marginBottom: spacing.xs || 12 }}
          />
          <Button
            title="LOG IN"
            variant="outline"
            onPress={() => navigation.navigate('Login')}
          />
        </Animated.View>

      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  centerWrapper: {
    flex: 1,
    width: '100%',
    maxWidth: 640,
    paddingHorizontal: 28,
    paddingTop: 12,
    paddingBottom: 24,
    justifyContent: 'space-between',
  },
  topBrand: {
    alignItems: 'flex-start',
    paddingVertical: 12,
  },
  brandText: {
    fontSize: 20,
    fontWeight: '900',
    letterSpacing: 3,
  },
  hero: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'flex-start',
    paddingVertical: 20,
  },
  line3Container: {
    minHeight: 56,
    justifyContent: 'center',
    alignItems: 'flex-start',
  },
  actions: {
    width: '100%',
    maxWidth: 400,
    alignSelf: 'center',
    paddingBottom: 12,
  },
});