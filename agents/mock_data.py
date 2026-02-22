"""
Mock data for testing pipeline without calling external APIs
"""

MOCK_BA_CHUNK1 = {
    "ekranlar": [
        {
            "ekran_adi": "Login Ekranı",
            "aciklama": "Kullanıcının email ve şifre ile sisteme giriş yapabileceği ekran. Şifre sıfırlama işlevini destekler.",
            "gerekli_dokumanlar": {
                "teknik_akis": "Login akış diyagramı gereklidir",
                "tasarim_dosyasi": "Figma - Login Screen Design v2.0"
            },
            "is_akisi_diyagrami": [
                "1. Kullanıcı login sayfasına gider",
                "2. Email adresini girer",
                "3. Şifresini girer",
                "4. Giriş Yap butonuna tıklar",
                "5. Sistem bilgileri doğrular",
                "6. Başarılı ise ana sayfaya yönlendirilir",
                "7. Hatalı ise uyarı mesajı gösterilir"
            ],
            "fonksiyonel_gereksinimler": [
                {
                    "id": "FR-01",
                    "tanim": "Kullanıcı email adresi girebilmelidir"
                },
                {
                    "id": "FR-02",
                    "tanim": "Kullanıcı şifre girebilmelidir"
                },
                {
                    "id": "FR-03",
                    "tanim": "Giriş Yap butonu tıklanabilir olmalıdır"
                },
                {
                    "id": "FR-04",
                    "tanim": "Şifremi Unuttum linki görünür ve tıklanabilir olmalıdır"
                },
                {
                    "id": "FR-05",
                    "tanim": "Hatalı giriş denemesinde kullanıcıya bilgilendirici hata mesajı gösterilmelidir"
                }
            ]
        }
    ]
}

MOCK_BA_CHUNK2 = {
    "ekran_detaylari": [
        {
            "ekran_adi": "Login Ekranı",
            "is_kurallari": [
                {
                    "kural": "3 başarısız giriş denemesinden sonra hesap 15 dakika bloklanır",
                    "detay": "Brute force saldırılarını önlemek için"
                },
                {
                    "kural": "Şifre minimum 8 karakter olmalıdır",
                    "detay": "Güvenlik standardı gereği"
                },
                {
                    "kural": "Email formatı geçerli olmalıdır",
                    "detay": "@ ve domain içermelidir"
                }
            ],
            "kabul_kriterleri": [
                {
                    "id": "BR-01",
                    "kriter": "Geçerli email ve şifre ile giriş başarılı olmalıdır"
                },
                {
                    "id": "BR-02",
                    "kriter": "Hatalı email veya şifre ile giriş engellenmelidir"
                },
                {
                    "id": "BR-03",
                    "kriter": "3 hatalı denemeden sonra 'Hesap bloklandı' mesajı gösterilmelidir"
                },
                {
                    "id": "BR-04",
                    "kriter": "Şifremi Unuttum linki şifre sıfırlama sayfasına yönlendirmelidir"
                }
            ],
            "validasyonlar": [
                {
                    "alan": "email",
                    "kisit": "Email formatı (@domain.com)",
                    "hata_mesaji": "Geçerli bir email adresi giriniz"
                },
                {
                    "alan": "email",
                    "kisit": "Zorunlu alan",
                    "hata_mesaji": "Email adresi boş bırakılamaz"
                },
                {
                    "alan": "password",
                    "kisit": "Minimum 8 karakter",
                    "hata_mesaji": "Şifre en az 8 karakter olmalıdır"
                },
                {
                    "alan": "password",
                    "kisit": "Zorunlu alan",
                    "hata_mesaji": "Şifre boş bırakılamaz"
                }
            ]
        }
    ]
}

MOCK_TA = {
    "teknik_analiz": {
        "genel_tanim": {
            "modul_adi": "Kullanıcı Authentication Modülü",
            "teknoloji_stack": ["React 18", "FastAPI", "PostgreSQL", "Redis", "JWT"],
            "mimari_yaklasim": "Microservices with REST API, JWT authentication, Redis session storage"
        },
        "endpoint_detaylari": {
            "/api/v1/auth/login": {
                "method": "POST",
                "aciklama": "Kullanıcı giriş endpoint'i. Email ve şifre alır, JWT token döner.",
                "request_body": {
                    "email": "string",
                    "password": "string",
                    "remember_me": "boolean (optional)"
                },
                "response_success": {
                    "access_token": "string (JWT)",
                    "refresh_token": "string",
                    "user": {
                        "id": "uuid",
                        "email": "string",
                        "name": "string"
                    }
                },
                "response_errors": [
                    {
                        "http_code": "401",
                        "error_code": "INVALID_CREDENTIALS",
                        "mesaj": "Email veya şifre hatalı"
                    },
                    {
                        "http_code": "423",
                        "error_code": "ACCOUNT_LOCKED",
                        "mesaj": "Hesap geçici olarak kilitlendi"
                    }
                ]
            }
        },
        "dto_veri_yapilari": [
            {
                "dto_adi": "LoginRequest",
                "aciklama": "Login endpoint'i için request DTO",
                "fields": [
                    {
                        "field": "email",
                        "tip": "string",
                        "validasyon": "required, email format"
                    },
                    {
                        "field": "password",
                        "tip": "string",
                        "validasyon": "required, min 8 chars"
                    }
                ]
            }
        ],
        "validasyon_kurallari": [
            {
                "id": "VR-01",
                "field": "email",
                "kural": "Email RFC 5322 standardına uygun olmalı"
            },
            {
                "id": "VR-02",
                "field": "password",
                "kural": "Minimum 8 karakter, en az 1 büyük harf, 1 küçük harf, 1 rakam"
            }
        ],
        "mock_curl_ornekleri": [
            {
                "endpoint_adi": "POST /api/v1/auth/login",
                "curl": 'curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d \'{"email": "test@example.com", "password": "Test1234"}\''
            }
        ]
    }
}

MOCK_TC = {
    "test_cases": [
        {
            "test_case_id": "TC-001",
            "br_id": "BR-01",
            "priority": "High",
            "test_area": "Authentication",
            "testcase": "Geçerli email ve şifre ile başarılı giriş",
            "test_steps": "1. Login sayfasına git\n2. Email alanına 'test@example.com' gir\n3. Şifre alanına 'Test1234' gir\n4. Giriş Yap butonuna tıkla",
            "test_data": '{"email": "test@example.com", "password": "Test1234"}',
            "expected_result": "Kullanıcı başarıyla giriş yapar ve Dashboard sayfasına yönlendirilir"
        },
        {
            "test_case_id": "TC-002",
            "br_id": "BR-02",
            "priority": "High",
            "test_area": "Authentication",
            "testcase": "Hatalı şifre ile giriş denemesi",
            "test_steps": "1. Login sayfasına git\n2. Email alanına 'test@example.com' gir\n3. Şifre alanına 'WrongPassword' gir\n4. Giriş Yap butonuna tıkla",
            "test_data": '{"email": "test@example.com", "password": "WrongPassword"}',
            "expected_result": "Sistem 401 hatası döner. 'Email veya şifre hatalı' mesajı gösterilir"
        },
        {
            "test_case_id": "TC-003",
            "br_id": "BR-03",
            "priority": "High",
            "test_area": "Security",
            "testcase": "3 başarısız denemeden sonra hesap kilitleme",
            "test_steps": "1. Login sayfasına git\n2. 3 kez hatalı şifre ile giriş dene\n3. 4. denemede hesap kilitleme mesajını doğrula",
            "test_data": '{"email": "test@example.com", "wrong_attempts": 3}',
            "expected_result": "3. denemeden sonra 423 hatası döner. 'Hesap geçici olarak kilitlendi' mesajı gösterilir"
        },
        {
            "test_case_id": "TC-004",
            "br_id": "BR-01",
            "priority": "Medium",
            "test_area": "Validation",
            "testcase": "Email formatı validasyonu",
            "test_steps": "1. Login sayfasına git\n2. Email alanına geçersiz format gir\n3. Şifre gir\n4. Giriş Yap'a tıkla",
            "test_data": '{"email": "notanemail", "password": "Test1234"}',
            "expected_result": "'Geçerli bir email adresi giriniz' mesajı gösterilir"
        },
        {
            "test_case_id": "TC-005",
            "br_id": "BR-04",
            "priority": "Medium",
            "test_area": "Password Reset",
            "testcase": "Şifremi Unuttum linki çalışması",
            "test_steps": "1. Login sayfasına git\n2. 'Şifremi Unuttum' linkine tıkla\n3. Şifre sıfırlama sayfasına yönlendirildiğini doğrula",
            "test_data": "{}",
            "expected_result": "Kullanıcı /forgot-password sayfasına yönlendirilir"
        },
        {
            "test_case_id": "TC-006",
            "br_id": "BR-01",
            "priority": "Low",
            "test_area": "UX",
            "testcase": "Şifre görünürlük toggle",
            "test_steps": "1. Login sayfasına git\n2. Şifre gir\n3. Göz ikonuna tıkla\n4. Şifrenin görünür olduğunu doğrula",
            "test_data": '{"password": "TestPass"}',
            "expected_result": "Şifre plain text olarak görünür hale gelir"
        },
        {
            "test_case_id": "TC-007",
            "br_id": "BR-01",
            "priority": "Medium",
            "test_area": "Session",
            "testcase": "Beni Hatırla özelliği",
            "test_steps": "1. Login sayfasına git\n2. Credentials gir\n3. Beni Hatırla checkbox'ını seç\n4. Giriş yap\n5. Browser'ı kapat ve tekrar aç",
            "test_data": '{"email": "test@example.com", "password": "Test1234", "remember_me": true}',
            "expected_result": "Kullanıcı otomatik giriş yapmış olmalı (session persist)"
        },
        {
            "test_case_id": "TC-008",
            "br_id": "BR-02",
            "priority": "Medium",
            "test_area": "Security",
            "testcase": "SQL Injection koruması",
            "test_steps": "1. Login sayfasına git\n2. Email alanına SQL injection payload gir\n3. Giriş Yap'a tıkla",
            "test_data": "{\"email\": \"admin'--\", \"password\": \"anything\"}",
            "expected_result": "Giriş başarısız olur, sistem güvenlik riski oluşmaz"
        },
        {
            "test_case_id": "TC-009",
            "br_id": "BR-01",
            "priority": "Low",
            "test_area": "Performance",
            "testcase": "Login response time",
            "test_steps": "1. Login sayfasına git\n2. Valid credentials gir\n3. Response time'ı ölç",
            "test_data": '{"email": "test@example.com", "password": "Test1234"}',
            "expected_result": "Response time < 500ms olmalı"
        },
        {
            "test_case_id": "TC-010",
            "br_id": "BR-03",
            "priority": "High",
            "test_area": "Security",
            "testcase": "Hesap kilitleme süresi kontrolü",
            "test_steps": "1. 3 kez hatalı giriş yap\n2. Hesap kilitlendiğini doğrula\n3. 15 dakika bekle\n4. Valid credentials ile giriş dene",
            "test_data": '{"wait_minutes": 15}',
            "expected_result": "15 dakika sonra hesap otomatik unlock olur, giriş başarılı olur"
        }
    ]
}

MOCK_BA_QA = {
    "score": 85,
    "passed": True,
    "feedback": {
        "strengths": [
            "Ekranlar detaylı tanımlanmış",
            "Fonksiyonel gereksinimler net",
            "İş kuralları açık"
        ],
        "weaknesses": [
            "Hata senaryoları daha detaylandırılabilir",
            "UI mockup'lar eklenebilir"
        ],
        "recommendations": [
            "Şifremi unuttum akışı detaylandırılmalı",
            "2FA desteği değerlendirilmeli"
        ]
    }
}

MOCK_TA_QA = {
    "score": 90,
    "passed": True,
    "feedback": {
        "strengths": [
            "Mimari tasarım sağlam",
            "Güvenlik önlemleri kapsamlı",
            "API design RESTful"
        ],
        "weaknesses": [
            "Rate limiting detayları eksik",
            "Error handling stratejisi belirtilmemiş"
        ],
        "recommendations": [
            "Logging ve monitoring eklenebilir",
            "API versioning stratejisi belirlenebilir"
        ]
    }
}

MOCK_TC_QA = {
    "score": 80,
    "passed": True,
    "feedback": {
        "strengths": [
            "Kritik senaryolar kapsanmış",
            "Test adımları net",
            "Öncelikler belirlenmiş"
        ],
        "weaknesses": [
            "Negatif test senaryoları az",
            "Performance test case'leri yok",
            "Beni hatırla özelliği test edilmemiş"
        ],
        "recommendations": [
            "Edge case'ler eklenebilir",
            "Load testing senaryoları eklenebilir",
            "Cross-browser test case'leri eklenebilir"
        ]
    }
}
