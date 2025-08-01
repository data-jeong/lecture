# 24. Computer Vision - 컴퓨터 비전

## 📚 과정 소개
광고 크리에이티브 분석, 자동 이미지 태깅, 브랜드 로고 인식, 광고 성과 예측을 위한 컴퓨터 비전 기술을 마스터합니다.

## 🎯 학습 목표
- 광고 이미지 자동 분석 및 태깅
- 브랜드 로고 인식 시스템
- 크리에이티브 성과 예측 모델
- 이미지 기반 타겟팅 시스템

## 📖 주요 내용

### 광고 크리에이티브 분석
```python
import cv2
import numpy as np
from tensorflow.keras.applications import ResNet50, VGG16
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
import torch
import torchvision.transforms as transforms
from PIL import Image
import matplotlib.pyplot as plt

class AdCreativeAnalyzer:
    """광고 크리에이티브 분석기"""
    
    def __init__(self):
        # 사전 훈련된 모델 로드
        self.resnet_model = ResNet50(weights='imagenet')
        self.feature_extractor = ResNet50(weights='imagenet', include_top=False, pooling='avg')
        
        # 이미지 전처리 파이프라인
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def analyze_creative_elements(self, image_path: str) -> dict:
        """크리에이티브 요소 분석"""
        # 이미지 로드
        img = cv2.imread(image_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 다양한 분석 수행
        analysis = {
            'color_analysis': self._analyze_colors(img_rgb),
            'object_detection': self._detect_objects(img_rgb),
            'text_detection': self._detect_text(img),
            'composition_analysis': self._analyze_composition(img_rgb),
            'emotional_tone': self._analyze_emotional_tone(img_rgb),
            'brand_elements': self._detect_brand_elements(img_rgb)
        }
        
        return analysis
    
    def _analyze_colors(self, img: np.ndarray) -> dict:
        """색상 분석"""
        # 주요 색상 추출
        pixels = img.reshape(-1, 3)
        from sklearn.cluster import KMeans
        
        kmeans = KMeans(n_clusters=5, random_state=42)
        kmeans.fit(pixels)
        
        colors = kmeans.cluster_centers_.astype(int)
        percentages = np.bincount(kmeans.labels_) / len(kmeans.labels_)
        
        # 색상 온도 계산
        avg_color = np.mean(pixels, axis=0)
        color_temp = self._calculate_color_temperature(avg_color)
        
        # 채도 및 밝기 분석
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        saturation = np.mean(hsv[:, :, 1])
        brightness = np.mean(hsv[:, :, 2])
        
        return {
            'dominant_colors': [tuple(color) for color in colors],
            'color_percentages': percentages.tolist(),
            'color_temperature': color_temp,
            'average_saturation': float(saturation),
            'average_brightness': float(brightness),
            'color_harmony': self._assess_color_harmony(colors)
        }
    
    def _detect_objects(self, img: np.ndarray) -> dict:
        """객체 감지"""
        # ResNet으로 이미지 분류
        img_resized = cv2.resize(img, (224, 224))
        img_array = np.expand_dims(img_resized, axis=0)
        img_preprocessed = preprocess_input(img_array)
        
        predictions = self.resnet_model.predict(img_preprocessed)
        decoded_predictions = decode_predictions(predictions, top=5)[0]
        
        detected_objects = []
        for _, class_name, confidence in decoded_predictions:
            detected_objects.append({
                'object': class_name,
                'confidence': float(confidence),
                'category': self._categorize_object(class_name)
            })
        
        return {
            'detected_objects': detected_objects,
            'main_subject': detected_objects[0]['object'] if detected_objects else None,
            'object_diversity': len(set([obj['category'] for obj in detected_objects]))
        }
    
    def _detect_text(self, img: np.ndarray) -> dict:
        """텍스트 감지 (OCR)"""
        import pytesseract
        
        # 그레이스케일 변환
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 텍스트 영역 감지
        text_areas = pytesseract.image_to_boxes(gray)
        detected_text = pytesseract.image_to_string(gray, lang='kor+eng')
        
        # 텍스트 특성 분석
        text_lines = [line.strip() for line in detected_text.split('\n') if line.strip()]
        
        return {
            'detected_text': detected_text,
            'text_lines': text_lines,
            'text_count': len(text_lines),
            'text_density': len(detected_text) / (img.shape[0] * img.shape[1]) * 10000,
            'has_call_to_action': self._detect_cta(detected_text),
            'language': self._detect_language(detected_text)
        }
    
    def _analyze_composition(self, img: np.ndarray) -> dict:
        """구도 분석"""
        h, w = img.shape[:2]
        
        # 삼등분할 분석
        rule_of_thirds_score = self._calculate_rule_of_thirds(img)
        
        # 대칭성 분석
        symmetry_score = self._calculate_symmetry(img)
        
        # 시각적 균형 분석
        balance_score = self._calculate_visual_balance(img)
        
        # 여백 분석
        whitespace_ratio = self._calculate_whitespace_ratio(img)
        
        return {
            'rule_of_thirds_score': rule_of_thirds_score,
            'symmetry_score': symmetry_score,
            'visual_balance': balance_score,
            'whitespace_ratio': whitespace_ratio,
            'aspect_ratio': w / h,
            'composition_quality': (rule_of_thirds_score + symmetry_score + balance_score) / 3
        }
    
    def _analyze_emotional_tone(self, img: np.ndarray) -> dict:
        """감정적 톤 분석"""
        # 색상 기반 감정 분석
        avg_color = np.mean(img.reshape(-1, 3), axis=0)
        
        # HSV 변환으로 감정 톤 분석
        hsv_avg = cv2.cvtColor(np.uint8([[avg_color]]), cv2.COLOR_RGB2HSV)[0][0]
        
        emotions = {
            'warmth': self._calculate_warmth(avg_color),
            'energy': self._calculate_energy(hsv_avg),
            'professionalism': self._calculate_professionalism(img),
            'friendliness': self._calculate_friendliness(img),
            'trustworthiness': self._calculate_trustworthiness(img)
        }
        
        # 주요 감정 톤
        dominant_emotion = max(emotions, key=emotions.get)
        
        return {
            'emotional_scores': emotions,
            'dominant_emotion': dominant_emotion,
            'emotion_intensity': emotions[dominant_emotion],
            'emotional_balance': np.std(list(emotions.values()))
        }
    
    def _detect_brand_elements(self, img: np.ndarray) -> dict:
        """브랜드 요소 감지"""
        # 로고 감지 (템플릿 매칭)
        logo_detected = self._detect_logos(img)
        
        # 브랜드 색상 감지
        brand_colors = self._detect_brand_colors(img)
        
        # 폰트 스타일 분석
        font_analysis = self._analyze_fonts(img)
        
        return {
            'logo_detected': logo_detected,
            'brand_colors': brand_colors,
            'font_style': font_analysis,
            'brand_consistency': self._calculate_brand_consistency(logo_detected, brand_colors),
            'brand_visibility': self._calculate_brand_visibility(img)
        }

class CreativePerformancePredictor:
    """크리에이티브 성과 예측기"""
    
    def __init__(self):
        self.analyzer = AdCreativeAnalyzer()
        self.model = self._build_performance_model()
        
    def _build_performance_model(self):
        """성과 예측 모델 구축"""
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler
        
        # 실제 환경에서는 훈련된 모델을 로드
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        scaler = StandardScaler()
        
        return {'model': model, 'scaler': scaler}
    
    def predict_ctr(self, image_path: str, campaign_context: dict = None) -> dict:
        """CTR 예측"""
        # 크리에이티브 분석
        analysis = self.analyzer.analyze_creative_elements(image_path)
        
        # 특성 벡터 생성
        features = self._extract_features(analysis, campaign_context)
        
        # 예측 수행 (실제로는 훈련된 모델 사용)
        predicted_ctr = self._mock_prediction(features)
        
        # 개선 제안
        improvements = self._suggest_improvements(analysis, predicted_ctr)
        
        return {
            'predicted_ctr': predicted_ctr,
            'confidence': 0.85,  # 모델 신뢰도
            'performance_factors': self._identify_performance_factors(analysis),
            'improvement_suggestions': improvements,
            'benchmark_comparison': self._compare_with_benchmark(analysis)
        }
    
    def _extract_features(self, analysis: dict, context: dict = None) -> np.ndarray:
        """특성 벡터 추출"""
        features = []
        
        # 색상 특성
        color_features = [
            analysis['color_analysis']['average_saturation'],
            analysis['color_analysis']['average_brightness'],
            analysis['color_analysis']['color_temperature']
        ]
        features.extend(color_features)
        
        # 구도 특성
        composition_features = [
            analysis['composition_analysis']['rule_of_thirds_score'],
            analysis['composition_analysis']['symmetry_score'],
            analysis['composition_analysis']['visual_balance'],
            analysis['composition_analysis']['whitespace_ratio']
        ]
        features.extend(composition_features)
        
        # 텍스트 특성
        text_features = [
            analysis['text_detection']['text_count'],
            analysis['text_detection']['text_density'],
            1 if analysis['text_detection']['has_call_to_action'] else 0
        ]
        features.extend(text_features)
        
        # 감정 특성
        emotion_features = list(analysis['emotional_tone']['emotional_scores'].values())
        features.extend(emotion_features)
        
        # 브랜드 특성
        brand_features = [
            1 if analysis['brand_elements']['logo_detected'] else 0,
            analysis['brand_elements']['brand_consistency'],
            analysis['brand_elements']['brand_visibility']
        ]
        features.extend(brand_features)
        
        # 컨텍스트 특성 (캠페인 정보)
        if context:
            context_features = [
                context.get('target_age_group', 25) / 100,  # 정규화
                1 if context.get('device_type') == 'mobile' else 0,
                context.get('time_of_day', 12) / 24  # 정규화
            ]
            features.extend(context_features)
        
        return np.array(features)
    
    def _mock_prediction(self, features: np.ndarray) -> float:
        """모의 예측 (실제로는 훈련된 모델 사용)"""
        # 특성 기반 간단한 휴리스틱
        base_ctr = 0.02
        
        # 색상 효과
        if len(features) > 2 and features[1] > 0.7:  # 높은 밝기
            base_ctr *= 1.1
        
        # 구도 효과
        if len(features) > 5 and features[3] > 0.6:  # 좋은 구도
            base_ctr *= 1.15
        
        # 텍스트 효과
        if len(features) > 8 and features[8] > 0:  # CTA 존재
            base_ctr *= 1.2
        
        # 브랜드 효과
        if len(features) > 15 and features[15] > 0:  # 로고 존재
            base_ctr *= 1.05
        
        return min(base_ctr, 0.15)  # 최대 15% CTR
    
    def _suggest_improvements(self, analysis: dict, predicted_ctr: float) -> list:
        """개선 제안"""
        suggestions = []
        
        # 색상 개선
        if analysis['color_analysis']['average_saturation'] < 0.3:
            suggestions.append({
                'category': 'color',
                'suggestion': '색상 채도를 높여 시각적 임팩트를 증가시키세요',
                'impact': 'medium'
            })
        
        # 구도 개선
        if analysis['composition_analysis']['rule_of_thirds_score'] < 0.4:
            suggestions.append({
                'category': 'composition',
                'suggestion': '삼등분할의 법칙을 활용해 구도를 개선하세요',
                'impact': 'high'
            })
        
        # 텍스트 개선
        if not analysis['text_detection']['has_call_to_action']:
            suggestions.append({
                'category': 'text',
                'suggestion': '명확한 행동 유도 문구(CTA)를 추가하세요',
                'impact': 'high'
            })
        
        # 브랜드 개선
        if not analysis['brand_elements']['logo_detected']:
            suggestions.append({
                'category': 'brand',
                'suggestion': '브랜드 로고를 추가하여 인지도를 높이세요',
                'impact': 'medium'
            })
        
        return suggestions

class BrandLogoRecognizer:
    """브랜드 로고 인식 시스템"""
    
    def __init__(self):
        self.logo_templates = self._load_logo_templates()
        self.feature_matcher = cv2.SIFT_create()
        
    def _load_logo_templates(self) -> dict:
        """로고 템플릿 로드"""
        # 실제로는 데이터베이스나 파일에서 로드
        return {
            'nike': 'path/to/nike_logo.png',
            'adidas': 'path/to/adidas_logo.png',
            'coca_cola': 'path/to/cocacola_logo.png'
        }
    
    def recognize_logos(self, image_path: str) -> list:
        """로고 인식"""
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        detected_logos = []
        
        for brand, template_path in self.logo_templates.items():
            if self._template_exists(template_path):
                confidence, location = self._match_template(gray, template_path)
                
                if confidence > 0.7:  # 임계값
                    detected_logos.append({
                        'brand': brand,
                        'confidence': confidence,
                        'location': location,
                        'size': self._calculate_logo_size(location)
                    })
        
        return sorted(detected_logos, key=lambda x: x['confidence'], reverse=True)
    
    def _match_template(self, img: np.ndarray, template_path: str) -> tuple:
        """템플릿 매칭"""
        template = cv2.imread(template_path, 0)
        
        # 다중 스케일 매칭
        best_confidence = 0
        best_location = None
        
        for scale in np.linspace(0.2, 3.0, 20):
            resized_template = cv2.resize(template, None, fx=scale, fy=scale)
            
            if resized_template.shape[0] > img.shape[0] or resized_template.shape[1] > img.shape[1]:
                continue
            
            result = cv2.matchTemplate(img, resized_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_confidence:
                best_confidence = max_val
                best_location = {
                    'x': max_loc[0],
                    'y': max_loc[1],
                    'width': resized_template.shape[1],
                    'height': resized_template.shape[0]
                }
        
        return best_confidence, best_location

class ImageBasedTargeting:
    """이미지 기반 타겟팅 시스템"""
    
    def __init__(self):
        self.analyzer = AdCreativeAnalyzer()
        self.audience_profiles = self._load_audience_profiles()
        
    def _load_audience_profiles(self) -> dict:
        """오디언스 프로필 로드"""
        return {
            'young_professionals': {
                'preferred_colors': ['blue', 'gray', 'white'],
                'style_keywords': ['modern', 'clean', 'professional'],
                'emotional_tone': ['professionalism', 'trustworthiness']
            },
            'millennials': {
                'preferred_colors': ['bright', 'vibrant'],
                'style_keywords': ['trendy', 'social', 'authentic'],
                'emotional_tone': ['energy', 'friendliness']
            },
            'luxury_consumers': {
                'preferred_colors': ['black', 'gold', 'white'],
                'style_keywords': ['elegant', 'premium', 'exclusive'],
                'emotional_tone': ['professionalism', 'trustworthiness']
            }
        }
    
    def predict_audience_fit(self, image_path: str) -> dict:
        """이미지-오디언스 적합도 예측"""
        analysis = self.analyzer.analyze_creative_elements(image_path)
        
        audience_scores = {}
        
        for audience, profile in self.audience_profiles.items():
            score = self._calculate_fit_score(analysis, profile)
            audience_scores[audience] = score
        
        # 최적 오디언스 선택
        best_audience = max(audience_scores, key=audience_scores.get)
        
        return {
            'audience_scores': audience_scores,
            'recommended_audience': best_audience,
            'confidence': audience_scores[best_audience],
            'targeting_suggestions': self._generate_targeting_suggestions(analysis, best_audience)
        }
    
    def _calculate_fit_score(self, analysis: dict, profile: dict) -> float:
        """적합도 점수 계산"""
        score = 0.0
        
        # 색상 매칭
        dominant_colors = analysis['color_analysis']['dominant_colors']
        color_match = self._match_colors(dominant_colors, profile['preferred_colors'])
        score += color_match * 0.3
        
        # 감정 톤 매칭
        emotional_scores = analysis['emotional_tone']['emotional_scores']
        emotion_match = self._match_emotions(emotional_scores, profile['emotional_tone'])
        score += emotion_match * 0.4
        
        # 구도 품질
        composition_quality = analysis['composition_analysis']['composition_quality']
        score += composition_quality * 0.3
        
        return min(score, 1.0)
```

## 🚀 프로젝트
1. **AI 크리에이티브 분석 플랫폼**
2. **브랜드 모니터링 시스템**
3. **자동 이미지 태깅 및 분류**
4. **성과 예측 기반 크리에이티브 최적화**