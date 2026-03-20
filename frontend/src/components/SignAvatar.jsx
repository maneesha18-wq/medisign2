import React, { useEffect, useRef, useImperativeHandle, forwardRef, useState } from 'react';
import { SL_DB } from '../services/signGestures';

const SignAvatar = forwardRef((props, ref) => {
  const canvasRef = useRef(null);
  const stateRef = useRef({
    t: 0,
    signing: false,
    word: '',
    desc: '',
    hL: { x: 0, y: 0, a: 0, s: 0.3, hs: 'rest' },
    hR: { x: 0, y: 0, a: 0, s: 0.3, hs: 'rest' },
    tL: { x: -0.02, y: 0.25, a: 0.05, s: 0.3, hs: 'rest' },
    tR: { x: 0.02, y: 0.25, a: -0.05, s: 0.3, hs: 'rest' },
    head: { nod: 0, tilt: 0 },
    wordQueue: []
  });

  const signTimerRef = useRef(null);

  const lerp = (a, b, t) => a + (b - a) * t;

  const drawHand = (ctx, hx, hy, angle, spread, hs, MX, MY, W, H) => {
    const bx = MX + hx * W * 0.5;
    const by = (MY + 55) + hy * H * 0.5;
    ctx.save();
    ctx.translate(bx, by);
    ctx.rotate(angle);

    const dk = window.matchMedia('(prefers-color-scheme:dark)').matches;
    const skn = dk ? '#c07840' : '#c8844a';
    const skd = dk ? '#8a5020' : '#a06030';
    ctx.fillStyle = skn;
    ctx.strokeStyle = skd;
    ctx.lineWidth = 1;

    switch (hs) {
      case 'rest':
        ctx.beginPath(); ctx.ellipse(0, 0, 9, 13, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        for (let i = 0; i < 4; i++) {
          ctx.beginPath(); ctx.ellipse((i - 1.5) * 4.5, -11, 2.8, 6, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        }
        ctx.beginPath(); ctx.ellipse(-12, 2, 2.5, 5, -0.4, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        break;
      case 'B':
        ctx.beginPath(); ctx.ellipse(0, 0, 9, 13, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        for (let i = 0; i < 4; i++) {
          ctx.beginPath(); ctx.ellipse((i - 1.5) * 3.8, -14, 2.5, 8, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        }
        ctx.beginPath(); ctx.ellipse(-9, 4, 3, 5, 0.5, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        break;
      case 'flat':
        ctx.beginPath(); 
        if (ctx.roundRect) ctx.roundRect(-10, -2, 20, 14, 4);
        else ctx.rect(-10, -2, 20, 14);
        ctx.fill(); ctx.stroke();
        for (let i = 0; i < 4; i++) {
          ctx.beginPath(); ctx.ellipse(-6 + i * 4, -9, 2.5, 9, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        }
        ctx.beginPath(); ctx.ellipse(-12, 4, 2.5, 5, 0.5, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        break;
      case 'index':
        ctx.beginPath(); ctx.ellipse(0, 2, 9, 11, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        for (let i = 0; i < 3; i++) {
          ctx.beginPath(); ctx.ellipse(-2 + i * 4 + 4, -4, 3, 5, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        }
        ctx.beginPath(); ctx.ellipse(-4, -14, 3, 9, -0.1, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        ctx.beginPath(); ctx.ellipse(-11, 3, 2.5, 5, 0.4, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        break;
      case 'A':
        ctx.beginPath(); ctx.ellipse(0, 0, 10, 12, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        for (let i = 0; i < 4; i++) {
          ctx.beginPath(); ctx.arc(-5 + i * 3.5, -9, 2.5, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        }
        ctx.beginPath(); ctx.ellipse(-12, 2, 3, 6, 0.3, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        break;
      case 'C':
        ctx.beginPath();
        ctx.moveTo(-8, -12);
        ctx.quadraticCurveTo(14, -12, 14, 0);
        ctx.quadraticCurveTo(14, 12, -8, 12);
        ctx.lineTo(-8, 6);
        ctx.quadraticCurveTo(8, 6, 8, 0);
        ctx.quadraticCurveTo(8, -6, -8, -6);
        ctx.closePath(); ctx.fill(); ctx.stroke();
        ctx.beginPath(); ctx.ellipse(-10, -4, 3, 8, 0.2, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        break;
      case 'D':
        ctx.beginPath(); ctx.ellipse(0, 2, 9, 11, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        for (let i = 0; i < 3; i++) {
          ctx.beginPath(); ctx.ellipse((i - 1) * 4 + 4, -3, 3, 5, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        }
        ctx.beginPath(); ctx.ellipse(-3, -14, 3, 9, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        ctx.beginPath(); ctx.ellipse(-10, -10, 3, 5, 0.5, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        break;
      case 'mid':
        ctx.beginPath(); ctx.ellipse(0, 2, 9, 11, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        for (let i = 0; i < 4; i++) {
          const fy = (i === 1) ? -15 : -5;
          const ry = (i === 1) ? 10 : 5;
          ctx.beginPath(); ctx.ellipse(-2 + i * 4, fy, 3, ry, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        }
        ctx.beginPath(); ctx.ellipse(-11, 3, 2.5, 5, 0.4, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        break;
      case 'no1':
        ctx.beginPath(); ctx.ellipse(0, 2, 9, 11, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        ctx.beginPath(); ctx.ellipse(-4, -14, 3, 9, -0.1, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        ctx.beginPath(); ctx.ellipse(2, -14, 3, 9, 0.1, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        for (let i = 0; i < 2; i++) {
          ctx.beginPath(); ctx.ellipse(7 + i * 3.5, -4, 3, 5, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        }
        ctx.beginPath(); ctx.ellipse(-11, 3, 2.5, 5, 0.4, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        break;
      case 'palm':
        ctx.beginPath(); ctx.ellipse(0, 0, 10, 13, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        for (let i = 0; i < 4; i++) {
          ctx.beginPath(); ctx.ellipse(-5 + i * 3.5, -12, 2.5, 7, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        }
        ctx.beginPath(); ctx.ellipse(-12, 2, 2.5, 5, 0.5, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        break;
      default:
        ctx.beginPath(); ctx.ellipse(0, 0, 9, 12, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
    }

    ctx.fillStyle = '#0284c7'; ctx.globalAlpha = 0.6;
    ctx.beginPath(); ctx.arc(0, 0, 3, 0, Math.PI * 2); ctx.fill();
    ctx.globalAlpha = 1;
    ctx.restore();
  };

  useImperativeHandle(ref, () => ({
    signSentence: (text) => {
      const words = text.trim().split(/\s+/).filter(w => w.length > 1);
      if (!words.length) return;
      stateRef.current.wordQueue = words.slice(1);
      signWord(words[0]);
    }
  }));

  const applyFrame = (f) => {
    stateRef.current.tL = { x: f.lx || 0, y: f.ly || 0, a: f.la || 0, s: f.ls || 0.3, hs: f.lhs || 'rest' };
    stateRef.current.tR = { x: f.rx || 0, y: f.ry || 0, a: f.ra || 0, s: f.rs || 0.3, hs: f.rhs || 'rest' };
  };

  const signWord = (word) => {
    const key = word.toLowerCase().replace(/[^a-z]/g, '');
    const entry = SL_DB[key] || SL_DB.default;
    const frames = entry.frames;
    stateRef.current.signing = true;

    // Update parent if needed (e.g. for subtitles)
    if (props.onWordChange) props.onWordChange(word, entry.desc, entry.src);

    let fi = 0;
    if (signTimerRef.current) clearInterval(signTimerRef.current);
    signTimerRef.current = setInterval(() => {
      if (fi >= frames.length) {
        clearInterval(signTimerRef.current);
        if (stateRef.current.wordQueue.length > 0) {
          setTimeout(() => signWord(stateRef.current.wordQueue.shift()), 350);
        } else {
          setTimeout(() => {
            stateRef.current.signing = false;
            applyFrame({ lx: -0.02, ly: 0.25, la: 0.05, ls: 0.3, lhs: 'rest', rx: 0.02, ry: 0.25, ra: -0.05, rs: 0.3, rhs: 'rest' });
            if (props.onWordChange) props.onWordChange('—', 'Avatar ready. Press mic to speak.', 'SL');
          }, 400);
        }
        return;
      }
      applyFrame(frames[fi]);
      fi++;
    }, 540);
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    const MX = W / 2, MY = H / 2;

    let animationId;
    const renderLoop = (time) => {
      const t = time / 1000;
      stateRef.current.t = t;
      
      ctx.clearRect(0, 0, W, H);
      const dk = window.matchMedia('(prefers-color-scheme:dark)').matches;

      // stage background
      ctx.fillStyle = dk ? '#12161f' : '#eef2f7';
      ctx.beginPath(); 
      if (ctx.roundRect) ctx.roundRect(0, 0, W, H, 14);
      else ctx.rect(0, 0, W, H);
      ctx.fill();

      const breathe = Math.sin(t * 0.7) * 2.5;
      const headY = MY - 88 + breathe * 0.3 + stateRef.current.head.nod * 7;
      const bodyY = MY + 8 + breathe * 0.2;

      const coatFill = dk ? '#dde4ed' : '#f0f4f8';
      const coatStroke = dk ? '#9aaabb' : '#c8d4e0';

      // COAT / TORSO
      ctx.fillStyle = coatFill; ctx.strokeStyle = coatStroke; ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(MX - 52, bodyY - 30);
      ctx.lineTo(MX - 62, bodyY + 82);
      ctx.lineTo(MX + 62, bodyY + 82);
      ctx.lineTo(MX + 52, bodyY - 30);
      ctx.quadraticCurveTo(MX, bodyY - 48, MX - 52, bodyY - 30);
      ctx.fill(); ctx.stroke();

      // LAPELS
      ctx.fillStyle = dk ? '#c2c9d6' : '#e0e6ee';
      ctx.beginPath(); ctx.moveTo(MX - 10, bodyY - 26); ctx.lineTo(MX - 28, bodyY + 10); ctx.lineTo(MX, bodyY + 5); ctx.closePath(); ctx.fill(); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(MX + 10, bodyY - 26); ctx.lineTo(MX + 28, bodyY + 10); ctx.lineTo(MX, bodyY + 5); ctx.closePath(); ctx.fill(); ctx.stroke();

      // STETHOSCOPE
      ctx.strokeStyle = '#2a5298'; ctx.lineWidth = 2.5; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(MX - 14, bodyY - 14); ctx.quadraticCurveTo(MX - 22, bodyY + 12, MX - 8, bodyY + 24); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(MX + 14, bodyY - 14); ctx.quadraticCurveTo(MX + 22, bodyY + 12, MX + 8, bodyY + 24); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(MX - 8, bodyY + 24); ctx.quadraticCurveTo(MX, bodyY + 36, MX + 8, bodyY + 24); ctx.stroke();
      ctx.fillStyle = '#2a5298';
      ctx.beginPath(); ctx.arc(MX, bodyY + 36, 5, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#4a73b8';
      ctx.beginPath(); ctx.arc(MX - 22, bodyY + 10, 4, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(MX + 22, bodyY + 10, 4, 0, Math.PI * 2); ctx.fill();

      // COAT POCKET + RED CROSS
      ctx.fillStyle = coatFill; ctx.strokeStyle = coatStroke; ctx.lineWidth = 1;
      ctx.beginPath(); 
      if (ctx.roundRect) ctx.roundRect(MX + 24, bodyY + 22, 22, 18, 3);
      else ctx.rect(MX + 24, bodyY + 22, 22, 18);
      ctx.fill(); ctx.stroke();
      ctx.strokeStyle = '#e24b4a'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(MX + 32, bodyY + 26); ctx.lineTo(MX + 32, bodyY + 36); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(MX + 27, bodyY + 31); ctx.lineTo(MX + 37, bodyY + 31); ctx.stroke();

      // SCRUBS COLLAR
      ctx.fillStyle = '#3a6bc4'; ctx.strokeStyle = '#2a5298'; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.ellipse(MX, bodyY - 20, 12, 8, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();

      // COAT SLEEVES
      ctx.fillStyle = coatFill; ctx.strokeStyle = coatStroke; ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(MX - 52, bodyY - 26); ctx.quadraticCurveTo(MX - 74, bodyY + 22, MX - 70, bodyY + 72);
      ctx.lineTo(MX - 52, bodyY + 72); ctx.quadraticCurveTo(MX - 50, bodyY + 20, MX - 34, bodyY - 20);
      ctx.closePath(); ctx.fill(); ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(MX + 52, bodyY - 26); ctx.quadraticCurveTo(MX + 74, bodyY + 22, MX + 70, bodyY + 72);
      ctx.lineTo(MX + 52, bodyY + 72); ctx.quadraticCurveTo(MX + 50, bodyY + 20, MX + 34, bodyY - 20);
      ctx.closePath(); ctx.fill(); ctx.stroke();

      // WRISTS
      ctx.fillStyle = '#c8844a'; ctx.strokeStyle = '#a06030'; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.ellipse(MX - 64, bodyY + 74, 9, 15, -0.15, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
      ctx.beginPath(); ctx.ellipse(MX + 64, bodyY + 74, 9, 15, 0.15, 0, Math.PI * 2); ctx.fill(); ctx.stroke();

      // NECK
      ctx.beginPath(); ctx.ellipse(MX, headY + 35, 10, 14, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();

      // HEAD
      ctx.save();
      ctx.translate(MX, headY);
      ctx.rotate(stateRef.current.head.tilt * 0.08);
      ctx.fillStyle = '#c8844a'; ctx.strokeStyle = '#a06030'; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.ellipse(0, 0, 30, 36, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();

      // hair
      ctx.fillStyle = '#2a1a0a'; ctx.strokeStyle = '#1a0e05'; ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.ellipse(0, -22, 30, 18, 0, Math.PI, Math.PI * 2);
      ctx.quadraticCurveTo(32, -20, 30, 0);
      ctx.quadraticCurveTo(32, -28, 0, -34);
      ctx.quadraticCurveTo(-32, -28, -30, 0);
      ctx.quadraticCurveTo(-32, -20, -30, -22);
      ctx.closePath(); ctx.fill(); ctx.stroke();

      // eyes
      const blink = (Math.sin(t * 0.28) > 0.96) ? 0.12 : 1;
      const eyeCol = dk ? '#0a0a1a' : '#1a1a2e';
      [-10, 10].forEach(ex => {
        ctx.fillStyle = '#fff';
        ctx.beginPath(); ctx.ellipse(ex, -6, 6.5, 8.5 * blink, 0, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = eyeCol;
        ctx.beginPath(); ctx.ellipse(ex, -5, 4, 5.5 * blink, 0, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = '#fff';
        ctx.beginPath(); ctx.ellipse(ex + 2, -7, 1.5, 1.5 * blink, 0, 0, Math.PI * 2); ctx.fill();
      });

      // eyebrows
      ctx.strokeStyle = '#5a3010'; ctx.lineWidth = 2; ctx.lineCap = 'round';
      const bl = stateRef.current.signing ? -3 : 0;
      ctx.beginPath(); ctx.moveTo(-15, -17 + bl); ctx.quadraticCurveTo(-9, -21 + bl, -3, -18 + bl); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(3, -18 + bl); ctx.quadraticCurveTo(9, -21 + bl, 15, -17 + bl); ctx.stroke();

      // nose
      ctx.strokeStyle = '#a06030'; ctx.lineWidth = 1.2;
      ctx.beginPath(); ctx.moveTo(0, -2); ctx.quadraticCurveTo(4, 6, 2, 10); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(-4, 10); ctx.quadraticCurveTo(0, 14, 4, 10); ctx.stroke();

      // mouth
      const mo = stateRef.current.signing ? 3 : 0;
      ctx.strokeStyle = '#7a3810'; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(-8, 18); ctx.quadraticCurveTo(0, 22 + mo, 8, 18); ctx.stroke();
      if (stateRef.current.signing) {
        ctx.fillStyle = 'rgba(60,30,10,0.18)';
        ctx.beginPath(); ctx.ellipse(0, 20, 7, 4 + mo, 0, 0, Math.PI * 2); ctx.fill();
      }

      // glasses
      ctx.strokeStyle = dk ? '#888' : '#333'; ctx.lineWidth = 1;
      [-10, 10].forEach(ex => {
        ctx.beginPath(); ctx.ellipse(ex, -5, 10, 9, 0, 0, Math.PI * 2); ctx.stroke();
      });
      ctx.beginPath(); ctx.moveTo(0, -5); ctx.lineTo(0, -5); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(-30, -5); ctx.lineTo(-20, -5); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(20, -5); ctx.lineTo(30, -5); ctx.stroke();
      ctx.restore();

      // Hands
      const spd = stateRef.current.signing ? 0.14 : 0.06;
      ['x', 'y', 'a', 's'].forEach(k => {
        stateRef.current.hL[k] = lerp(stateRef.current.hL[k], stateRef.current.tL[k] || 0, spd);
        stateRef.current.hR[k] = lerp(stateRef.current.hR[k], stateRef.current.tR[k] || 0, spd);
      });
      stateRef.current.hL.hs = stateRef.current.tL.hs || 'rest';
      stateRef.current.hR.hs = stateRef.current.tR.hs || 'rest';

      drawHand(ctx, stateRef.current.hL.x, stateRef.current.hL.y, stateRef.current.hL.a, stateRef.current.hL.s, stateRef.current.hL.hs, MX, MY, W, H);
      drawHand(ctx, stateRef.current.hR.x, stateRef.current.hR.y, stateRef.current.hR.a, stateRef.current.hR.s, stateRef.current.hR.hs, MX, MY, W, H);

      if (stateRef.current.signing) {
        ctx.fillStyle = '#0284c7'; ctx.globalAlpha = 0.07;
        ctx.beginPath(); ctx.ellipse(MX, MY + 10, 100, 80, 0, 0, Math.PI * 2); ctx.fill();
        ctx.globalAlpha = 1;
        const p = Math.sin(t * 5) * 0.5 + 0.5;
        ctx.fillStyle = '#0284c7'; ctx.globalAlpha = 0.3 + p * 0.3;
        ctx.beginPath(); ctx.arc(MX + 92, headY - 20, 5, 0, Math.PI * 2); ctx.fill();
        ctx.globalAlpha = 1;
      }

      animationId = requestAnimationFrame(renderLoop);
    };

    animationId = requestAnimationFrame(renderLoop);

    return () => {
      cancelAnimationFrame(animationId);
      if (signTimerRef.current) clearInterval(signTimerRef.current);
    };
  }, []);

  return (
    <canvas 
      ref={canvasRef} 
      width={400} 
      height={310} 
      className="max-w-full rounded-xl"
    />
  );
});

export default SignAvatar;
