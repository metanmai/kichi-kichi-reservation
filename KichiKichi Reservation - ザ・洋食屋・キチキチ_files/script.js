document.addEventListener('DOMContentLoaded', () => {
    const reservationMessage = document.getElementById('reservation-message');

    const languageMessages = {
    en: `Reservation Success : Once the reservation is complete, you will be redirected to the reservation confirmation page (https://kichikichi.com/kichikichi-reservation-confirmation-and-cancelation-page/).\nPlease note: You will not receive a confirmation email.\n\nReservation Failure: If the reservation fails, you will remain on the reservation input page and see a message stating "This time slot is fully booked."`,

    ja: `予約成功時    : 予約が完了すると、予約確認ページ(https://kichikichi.com/kichikichi-reservation-confirmation-and-cancelation-page/）に遷移します。なお、予約完了メールは送信されません。\n\n予約失敗時    : 予約に失敗すると、予約を入力したページから遷移せず、「この時間枠は満席となりました。」と表示されます。`,

    ko: `예약 성공 시 : 예약이 완료되면 예약 확인 페이지(https://kichikichi.com/kichikichi-reservation-confirmation-and-cancelation-page/)로 리디렉션됩니다.\n주의: 확인 이메일은 발송되지 않습니다.\n\n예약 실패 시 : 예약에 실패하면 예약 입력 페이지에서 벗어나지 않고 "이 시간대는 예약이 가득 찼습니다"라는 메시지가 표시됩니다.`,

    'zh-CN': `预订成功时    : 完成预订后，您将被重定向到预订确认页面(https://kichikichi.com/kichikichi-reservation-confirmation-and-cancelation-page/）。\n注意：完成后不会发送确认邮件。\n\n预订失败时    : 如果预订失败，您将停留在预订输入页面，并看到一条消息，显示“此时间段已满”。`,

    'zh-TW': `預約成功時    : 完成預約後，您將被重定向到預約確認頁面(https://kichikichi.com/kichikichi-reservation-confirmation-and-cancelation-page/）。\n注意：完成後不會寄送確認郵件。\n\n預約失敗時    : 如果預約失敗，您將停留在預約輸入頁面，並看到一條消息，顯示“此時間段已滿”。`
    };

    const languageTexts = {
        en: {
            agreeLabel: 'Please arrive by the arrival time. If you are not at the store by the arrival time, your reservation will be considered canceled.',
            nameLabel: 'Name',
            nameHint: '* Please enter your name using alphabet letters only.',
            emailLabel: 'Email Address',
            confirmEmailLabel: 'Confirm Email Address',
            numberOfPeopleLabel: 'Number of People',
            seatingPreferenceLabel: 'Seating Preference',
            seatingHint: '* Table seats will be shared.',
            seatingOptions: {
                Bar: 'Bar',
                Table: 'Table'
            },
            timeLabel: 'Reservation Time',
            timeHint: '* Please come to the front of the store by the arrival time.',
            confirmAgreeLabel: 'Please arrive by the arrival time. If you are not at the store by the arrival time, your reservation will be considered canceled.',
            confirmButton: 'Confirm',
            messages: {
                emailMismatch: 'The email addresses do not match.',
                fullyBooked: 'This time slot is fully booked.',
                reservationConfirmed: 'The reservation has been confirmed.',
                emailExists: "A reservation already exists with this email address."
            },
            no_available_slots: 'Fully booked for this condition'
        },
        ja: {
            agreeLabel: 'ご来店時間までにご来店下さい。ご来店時間に店頭に居られない場合は、キャンセルされたとみなします。',
            nameLabel: '名前',
            nameHint: '* 名前はアルファベットのみで入力してください。',
            emailLabel: 'メールアドレス',
            confirmEmailLabel: 'メールアドレス確認',
            numberOfPeopleLabel: '人数',
            seatingPreferenceLabel: '席の種類',
            seatingHint: '* テーブル席は相席となります。',
            seatingOptions: {
                Bar: 'カウンター',
                Table: 'テーブル'
            },
            timeLabel: '予約時間',
            timeHint: '* ご来店時間までには店の前に来てください。',
            confirmAgreeLabel: 'ご来店時間までにご来店下さい。ご来店時間に店頭に居られない場合は、キャンセルされたとみなします。',
            confirmButton: '確定',
            messages: {
                emailMismatch: 'メールアドレスが一致しません。',
                fullyBooked: 'この時間枠は満席となりました。',
                reservationConfirmed: '予約が確定しました。',
                emailExists: "すでにこのメールアドレスで予約が存在します。"
            },
            no_available_slots: 'この条件では満席です'
        },
        ko: {
            agreeLabel: '도착 시간까지 도착해 주세요. 도착 시간에 매장에 없으면 예약이 취소된 것으로 간주됩니다.',
            nameLabel: '이름',
            nameHint: '* 이름은 알파벳 문자로만 입력하세요.',
            emailLabel: '이메일 주소',
            confirmEmailLabel: '이메일 주소 확인',
            numberOfPeopleLabel: '인원수',
            seatingPreferenceLabel: '좌석 유형',
            seatingHint: '* 테이블 좌석은 합석이 됩니다.',
            seatingOptions: {
                Bar: '카운터',
                Table: '테이블'
            },
            timeLabel: '예약 시간',
            timeHint: '* 도착 시간까지 가게 앞에 와 주세요.',
            confirmAgreeLabel: '도착 시간까지 도착해 주세요. 도착 시간에 매장에 없으면 예약이 취소된 것으로 간주됩니다.',
            confirmButton: '확정',
            messages: {
                emailMismatch: '이메일 주소가 일치하지 않습니다。',
                fullyBooked: '이 시간대는 예약이 꽉 찼습니다。',
                reservationConfirmed: '예약이 확정되었습니다。',
                emailExists: "이 이메일 주소로 이미 예약이 존재합니다."
            },
            no_available_slots: '이 조건에서는 예약이 가득 찼습니다'
        },
        'zh-CN': {
            agreeLabel: '请在到店时间前到达。如果您在到店时间没有到店，将视为取消预约。',
            nameLabel: '姓名',
            nameHint: '* 请使用字母输入您的名字。',
            emailLabel: '电子邮件地址',
            confirmEmailLabel: '确认电子邮件地址',
            numberOfPeopleLabel: '人数',
            seatingPreferenceLabel: '座位类型',
            seatingHint: '* 桌位将会拼桌。',
            seatingOptions: {
                Bar: '吧台',
                Table: '桌子'
            },
            timeLabel: '预约时间',
            timeHint: '* 请在到店时间前到店前。',
            confirmAgreeLabel: '请在到店时间前到达。如果您在到店时间没有到店，将视为取消预约。',
            confirmButton: '确定',
            messages: {
                emailMismatch: '电子邮件地址不匹配。',
                fullyBooked: '此时间段已满。',
                reservationConfirmed: '预订已确认。',
                emailExists: "该邮箱地址已存在预订。"
            },
            no_available_slots: '该条件下已满员'
        },
        'zh-TW': {
            agreeLabel: '請在到店時間前到達。如果您在到店時間沒有到店，將視為取消預約。',
            nameLabel: '姓名',
            nameHint: '* 請使用字母輸入您的名字。',
            emailLabel: '電子郵件地址',
            confirmEmailLabel: '確認電子郵件地址',
            numberOfPeopleLabel: '人數',
            seatingPreferenceLabel: '座位類型',
            seatingHint: '* 桌位將會拼桌。',
            seatingOptions: {
                Bar: '吧台',
                Table: '桌子'
            },
            timeLabel: '預約時間',
            timeHint: '* 請在到店時間前到店前。',
            confirmAgreeLabel: '請在到店時間前到達。如果您在到店時間沒有到店，將視為取消預約。',
            confirmButton: '確定',
            messages: {
                emailMismatch: '電子郵件地址不匹配。',
                fullyBooked: '此時間段已滿。',
                reservationConfirmed: '預訂已確認。',
                emailExists: "此電子郵件地址已有預約。"
            },
            no_available_slots: '此條件下已滿位'
        }
    };

    const timeSlots = {
        en: {
            'slot_1': 'Arrival Time: 11:40 A.M. (Seating Time: 0:00 P.M. - 1:00 P.M.)',
            'slot_2': 'Arrival Time: 0:40 P.M. (Seating Time: 1:00 P.M. - 2:00 P.M.)',
            'slot_3': 'Arrival Time: 4:40 P.M. (Seating Time: 5:00 P.M. - 6:00 P.M.)',
            'slot_4': 'Arrival Time: 5:40 P.M. (Seating Time: 6:00 P.M. - 7:00 P.M.)',
            'slot_5': 'Arrival Time: 6:40 P.M. (Seating Time: 7:00 P.M. - 8:00 P.M.)',
            'slot_6': 'Arrival Time: 7:40 P.M. (Seating Time: 8:00 P.M. - 9:00 P.M.)'
        },
        ja: {
            'slot_1': 'ご来店時間: 11:40 A.M.（お席時間: 0:00 P.M. - 1:00 P.M.）',
            'slot_2': 'ご来店時間: 0:40 P.M.（お席時間: 1:00 P.M. - 2:00 P.M.）',
            'slot_3': 'ご来店時間: 4:40 P.M.（お席時間: 5:00 P.M. - 6:00 P.M.）',
            'slot_4': 'ご来店時間: 5:40 P.M.（お席時間: 6:00 P.M. - 7:00 P.M.）',
            'slot_5': 'ご来店時間: 6:40 P.M.（お席時間: 7:00 P.M. - 8:00 P.M.）',
            'slot_6': 'ご来店時間: 7:40 P.M.（お席時間: 8:00 P.M. - 9:00 P.M.）'
        },
        ko: {
            'slot_1': '도착 시간: 11:40 A.M. (착석 시간: 0:00 P.M. - 1:00 P.M.)',
            'slot_2': '도착 시간: 0:40 P.M. (착석 시간: 1:00 P.M. - 2:00 P.M.)',
            'slot_3': '도착 시간: 4:40 P.M. (착석 시간: 5:00 P.M. - 6:00 P.M.)',
            'slot_4': '도착 시간: 5:40 P.M. (착석 시간: 6:00 P.M. - 7:00 P.M.)',
            'slot_5': '도착 시간: 6:40 P.M. (착석 시간: 7:00 P.M. - 8:00 P.M.)',
            'slot_6': '도착 시간: 7:40 P.M. (착석 시간: 8:00 P.M. - 9:00 P.M.)'
        },
        'zh-CN': {
            'slot_1': '到店时间: 11:40 A.M. (入座时间: 0:00 P.M. - 1:00 P.M.)',
            'slot_2': '到店时间: 0:40 P.M. (入座时间: 1:00 P.M. - 2:00 P.M.)',
            'slot_3': '到店时间: 4:40 P.M. (入座时间: 5:00 P.M. - 6:00 P.M.)',
            'slot_4': '到店时间: 5:40 P.M. (入座时间: 6:00 P.M. - 7:00 P.M.)',
            'slot_5': '到店时间: 6:40 P.M. (入座时间: 7:00 P.M. - 8:00 P.M.)',
            'slot_6': '到店时间: 7:40 P.M. (入座时间: 8:00 P.M. - 9:00 P.M.)'
        },
        'zh-TW': {
            'slot_1': '到店時間: 11:40 A.M. (入座時間: 0:00 P.M. - 1:00 P.M.)',
            'slot_2': '到店時間: 0:40 P.M. (入座時間: 1:00 P.M. - 2:00 P.M.)',
            'slot_3': '到店時間: 4:40 P.M. (入座時間: 5:00 P.M. - 6:00 P.M.)',
            'slot_4': '到店時間: 5:40 P.M. (入座時間: 6:00 P.M. - 7:00 P.M.)',
            'slot_5': '到店時間: 6:40 P.M. (入座時間: 7:00 P.M. - 8:00 P.M.)',
            'slot_6': '到店時間: 7:40 P.M. (入座時間: 8:00 P.M. - 9:00 P.M.)'
        }
    };

    // 言語に基づいたテキストとスロットの更新
    const setTextsForLanguage = (lang) => {
        const texts = languageTexts[lang];
        document.getElementById('agree-label').textContent = texts.agreeLabel;
        document.getElementById('name-label').textContent = texts.nameLabel;
        document.getElementById('name-hint').textContent = texts.nameHint;
        document.getElementById('email-label').textContent = texts.emailLabel;
        document.getElementById('confirm-email-label').textContent = texts.confirmEmailLabel;
        document.getElementById('number-of-people-label').textContent = texts.numberOfPeopleLabel;
        document.getElementById('seating-preference-label').textContent = texts.seatingPreferenceLabel;
        document.getElementById('seating-hint').textContent = texts.seatingHint;
        document.getElementById('time-label').textContent = texts.timeLabel;
        document.getElementById('time-hint').textContent = texts.timeHint;
        document.getElementById('confirm-agree-label').textContent = texts.confirmAgreeLabel;
        document.getElementById('submit-button').textContent = texts.confirmButton;
        document.getElementById('close-reservation-modal').addEventListener('click', function () {
            document.getElementById('reservation-modal').classList.add('hidden');
            document.getElementById('reservation-modal-message').textContent = '';
        });
        

        // 座席オプションの更新
        const seatingPreferenceSelect = document.getElementById('seating_preference');
        seatingPreferenceSelect.innerHTML = `<option value="" disabled selected>Select Seat</option>`;
        for (const [value, label] of Object.entries(texts.seatingOptions)) {
            seatingPreferenceSelect.innerHTML += `<option value="${value}">${label}</option>`;
        }

        // 時間枠の更新
        const timeSelect = document.getElementById('time');
        timeSelect.innerHTML = `<option value="" disabled selected>Select Time Slot</option>`;
        for (const [value, label] of Object.entries(timeSlots[lang])) {
            timeSelect.innerHTML += `<option value="${value}">${label}</option>`;
        }

        // メッセージの更新
        reservationMessage.innerHTML = languageMessages[lang];
    };

    const languageSelect = document.getElementById('language-select');
    languageSelect.addEventListener('change', () => {
        const selectedLang = languageSelect.value;
        setTextsForLanguage(selectedLang);
    
        // #agreeを除外して制御
        const inputs = document.querySelectorAll('#reservation-form input[type="text"], #reservation-form input[type="email"], #reservation-form input[type="number"], #reservation-form select');
        inputs.forEach(input => {
            input.disabled = !selectedLang;
        });
    
        // #agreeは常にenabledにする
        const agreeCheckbox = document.getElementById('agree');
        agreeCheckbox.disabled = false;
    
        checkFormFilled();
    });
    

    const checkFormFilled = () => {
        const requiredFields = document.querySelectorAll('#reservation-form [required]');
        let allFilled = true;
        requiredFields.forEach(field => {
            if (!field.value || !document.getElementById('agree').checked || !document.getElementById('language-select').value) {
                allFilled = false;
            }
        });
        const confirmAgree = document.getElementById('confirm-agree');
        confirmAgree.disabled = !allFilled;
        const submitButton = document.getElementById('submit-button');
        submitButton.disabled = !confirmAgree.checked;
        submitButton.style.backgroundColor = confirmAgree.checked ? '#ffff33' : '#cccccc';
        submitButton.style.cursor = confirmAgree.checked ? 'pointer' : 'not-allowed';
    };

    const agreeCheckbox = document.getElementById('agree');
    agreeCheckbox.addEventListener('change', () => {
        const inputs = document.querySelectorAll('#reservation-form input[type="text"], #reservation-form input[type="email"], #reservation-form input[type="number"], #reservation-form select');
        inputs.forEach(input => {
            if (document.getElementById('language-select').value) {
                input.disabled = !agreeCheckbox.checked;
            }
        });
        checkFormFilled();
    });

    const confirmAgreeCheckbox = document.getElementById('confirm-agree');
    confirmAgreeCheckbox.addEventListener('change', () => {
        const submitButton = document.getElementById('submit-button');
        submitButton.disabled = !confirmAgreeCheckbox.checked;
        submitButton.style.backgroundColor = confirmAgreeCheckbox.checked ? '#ffff33' : '#cccccc';
        submitButton.style.cursor = confirmAgreeCheckbox.checked ? 'pointer' : 'not-allowed';
    });

    const inputs = document.querySelectorAll('#reservation-form input[type="text"], #reservation-form input[type="email"], #reservation-form input[type="number"], #reservation-form select');
    inputs.forEach(input => {
        input.addEventListener('input', checkFormFilled);
    });

    checkFormFilled();

    const updateAvailableTimeSlots = () => {
        const numPeople = $('#number_of_people').val().trim();
        const seatingPreference = $('#seating_preference').val();
        const selectedLang = $('#language-select').val() || 'ja';
    
        if (numPeople && seatingPreference) {
            $.ajax({
                type: 'POST',
                url: reservation.ajax_url,
                data: {
                    action: 'get_available_time_slots',
                    number_of_people: numPeople,
                    seating_preference: seatingPreference,
                    language: selectedLang
                },
                success: function(response) {
                    if (response.success) {
                        $.ajax({
                            type: 'POST',
                            url: reservation.ajax_url,
                            data: {
                                action: 'get_server_time'
                            },
                            success: function(serverResponse) {
                                if (serverResponse.success) {
                                    const serverTime = serverResponse.data.server_time;
                                    const currentHour = parseInt(serverTime.split(':')[0], 10);
    
                                    const timeSelect = $('#time');
                                    timeSelect.empty();
                                    timeSelect.append('<option value="">Select Time Slot</option>');
    
                                    const availableLabels = response.data;
                                    const slots = timeSlots[selectedLang];
    
                                    let allowedSlots = [];
    
                                    if (currentHour >= 9 && currentHour < 10) {
                                        allowedSlots = ['slot_1', 'slot_2'];
                                    } else if (currentHour >= 13 && currentHour < 14) {
                                        allowedSlots = ['slot_3', 'slot_4', 'slot_5', 'slot_6'];
                                    }
    
                                    if (allowedSlots.length > 0) {
                                        allowedSlots.forEach(slot => {
                                            const label = slots[slot];
                                            if (availableLabels.includes(label)) {
                                                timeSelect.append(`<option value="${slot}">${label}</option>`);
                                            }
                                        });
                                    }
    
                                    if (timeSelect.children('option').length === 1) {
                                        // 追加されたoptionがない場合
                                        const noSlotMessage = languageTexts[selectedLang].no_available_slots || "No available slots";
                                        timeSelect.append(`<option value="" disabled selected>${noSlotMessage}</option>`);
                                    }
                                }
                            },
                            error: function() {
                                console.error('Failed to fetch server time');
                            }
                        });
                    }
                },
                error: function(xhr, status, error) {
                    console.error("AJAX Error:", error);
                }
            });
        }
    };   
    
    // イベントリスナーを適用
    $('#number_of_people, #seating_preference').on('input change', updateAvailableTimeSlots);
    

    $('#reservation-form').on('submit', function(e) {
        e.preventDefault();

        const email = $('#email').val();
        const confirmEmail = $('#confirm_email').val();
        const selectedLang = document.getElementById('language-select').value;
        const messages = languageTexts[selectedLang].messages;

        // メールアドレスが一致しない場合
        if (email !== confirmEmail) {
            alert(messages.emailMismatch); // メールアドレス不一致のメッセージを表示
            return;
        }

        var selectedTime = $('#time').val();
        var numPeople = $('#number_of_people').val();
        var seatingPreference = $('#seating_preference').val();

        // 予約限界を確認するAjaxリクエスト
        $.ajax({
            type: 'POST',
            url: reservation.ajax_url,
            data: {
                action: 'check_reservation_limit',
                time: selectedTime,
                number_of_people: numPeople,
                seating_preference: seatingPreference
            },
            success: function(response) {
                // 予約が可能な場合
                if (response.success) {
                    // 予約を保存するAjaxリクエスト
                    $.ajax({
                        type: 'POST',
                        url: reservation.ajax_url,
                        data: {
                            action: 'save_reservation',
                            name: $('#name').val(),
                            email: $('#email').val(),
                            time: selectedTime,
                            seating_preference: $('#seating_preference').val(),
                            number_of_people: numPeople,
                            language: selectedLang
                        },
                        success: function(response) {
                            const modal = document.getElementById('reservation-modal');
                            const message = document.getElementById('reservation-modal-message');
                                               
                            if (response.success) {
                                message.textContent = messages.reservationConfirmed;
                                modal.classList.remove('hidden');
                                setTimeout(() => {
                                    window.location.href = "https://kichikichi.com/kichikichi-reservation-confirmation-and-cancelation-page/";
                                }, 2000);
                            } else if (response.data && response.data.error === 'email_exists') {
                                message.textContent = messages.emailExists || 'このメールアドレスでは既に予約されています。';
                                modal.classList.remove('hidden');
                            } else {
                                message.textContent = messages.fullyBooked || '満席です。';
                                modal.classList.remove('hidden');
                            }
                        }                                            
                    });
                } else {
                    const modal = document.getElementById('reservation-modal');
                    const message = document.getElementById('reservation-modal-message');
                    message.textContent = messages.fullyBooked || '満席です。';
                    modal.classList.remove('hidden');
                }
            }
        });
    });

    function loadReservationList() {
        $.ajax({
            type: 'POST',
            url: reservation.ajax_url,
            data: {
                action: 'load_reservation_list'
            },
            success: function(response) {
                if(response.success) {
                    $('#reservation-list').html(response.data.html);
                }
            }
        });
    }

    loadReservationList();
});