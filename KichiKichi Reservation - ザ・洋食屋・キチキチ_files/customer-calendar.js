jQuery(document).ready(function($) {

    // 日本標準時 (JST) での現在時刻を取得する関数
    function getJapanDate() {
        let now = new Date();
        let utc = now.getTime() + (now.getTimezoneOffset() * 60000);
        let jst = new Date(utc + (9 * 60 * 60 * 1000));
        return jst;
    }

    // 日本時間の現在日時
    let currentDate = getJapanDate();
    // 当日判定用：時分秒をリセット
    let today = new Date(currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate());
    let currentMonth = currentDate.getMonth();
    let currentYear = currentDate.getFullYear();
    let availableMonths = [];

    function loadAvailableMonths() {
        $.ajax({
            url: customer_calendar.ajax_url,
            method: 'POST',
            data: {
                action: 'get_available_calendar_months',
            },
            success: function(response) {
                availableMonths = (response.data || []).map(m => m.trim());
                if (availableMonths.length === 0) {
                    console.warn("データベースに登録された月がありません。");
                    $('#calendar-container').html("<p>営業日データがありません。</p>");
                    return;
                }
                updateMonthNavigation();
                loadCalendar(currentMonth, currentYear);
            },
            error: function(xhr, status, error) {
                console.error("AJAX Error:", error);
            }
        });
    }

    function loadCalendar(month, year) {
        let formattedMonth = `${year}-${String(month + 1).padStart(2, '0')}`; // 例："2025-04"
        if (!availableMonths.includes(formattedMonth)) {
            console.warn(`No data available for this month (${formattedMonth}).`);
            return;
        }
        $.ajax({
            url: customer_calendar.ajax_url,
            method: 'POST',
            data: {
                action: 'get_customer_calendar_data',
            },
            success: function(response) {
                let data = response.data || {};

                // カレンダー部分を描画
                $('#calendar-grid').empty();
                $('#calendar-month').text(formattedMonth);
                let daysInMonth = new Date(year, month + 1, 0).getDate();
                for (let day = 1; day <= daysInMonth; day++) {
                    // 各日の判定用に、時分秒をリセット
                    let calendarDate = new Date(year, month, day);
                    calendarDate.setHours(0, 0, 0, 0);

                    let additionalClass = "";
                    if (calendarDate < today) {
                        additionalClass = " past";
                    } else if (calendarDate.getTime() === today.getTime()) {
                        additionalClass = " today";
                    }
                    
                    let date = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                    // 各日のデータ。未定義の場合はデフォルト値を用いる
                    let entry = data[date] || { lunch: "Unknown", dinner: "Unknown" };
                    
                    let lunchClass = (entry.lunch === "Open") ? 'open' : 'closed';
                    let dinnerClass = (entry.dinner === "Open") ? 'open' : 'closed';

                    $('#calendar-grid').append(`
                        <div class="calendar-day${additionalClass}">
                            <span class="day-number">${day}</span>
                            <div class="meal lunch ${lunchClass}">
                                <span class="emoji-space">☀️</span><br /> ${entry.lunch}
                            </div>
                            <div class="meal dinner ${dinnerClass}">
                                <span class="emoji-space">🌙</span><br /> ${entry.dinner}
                            </div>
                        </div>
                    `);
                }

                // 画面下部に、本日の予約情報を描画（表示している月が本日の月の場合のみ）
                $('.today-reservation').remove(); // 前回分の情報があれば削除
                if (year === currentYear && month === currentMonth) {
                    let todayStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
                    let todayEntry = data[todayStr] || { lunch: "Unknown", dinner: "Unknown" };
                    
                    let lunchOpen = (todayEntry.lunch === "Open");
                    let dinnerOpen = (todayEntry.dinner === "Open");
                    let reservationMessage = "";
                    
                    if (lunchOpen && !dinnerOpen) {
                        reservationMessage = "Reservation: Lunch 9:00-10:00 AM";
                    } else if (!lunchOpen && dinnerOpen) {
                        reservationMessage = "Reservation: Dinner 1:00-2:00 PM";
                    } else if (lunchOpen && dinnerOpen) {
                        reservationMessage = "Reservation: Lunch 9:00-10:00 AM | Dinner 1:00-2:00 PM";
                    } else {
                        reservationMessage = "Closed Today";
                    }                    
                    
                    // 凡例の直後に本日の予約情報を追加
                    $('.calendar-legend').after(`
                        <div class="today-reservation">
                            <p>${reservationMessage}</p>
                        </div>
                    `);
                }
            },
            error: function(xhr, status, error) {
                console.error("Failed to fetch calendar data:", error);
            }
        });
    }

    function updateMonthNavigation() {
        let formattedMonth = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}`;
        $("#prev-month").prop("disabled", !availableMonths.includes(formattedMonth));
        $("#next-month").prop("disabled", !availableMonths.includes(formattedMonth));
    }

    $('#prev-month').click(function() {
        let prevMonth = currentMonth - 1;
        let prevYear = currentYear;
        if (prevMonth < 0) {
            prevMonth = 11;
            prevYear--;
        }
        let formattedMonth = `${prevYear}-${String(prevMonth + 1).padStart(2, '0')}`;
        if (availableMonths.includes(formattedMonth)) {
            currentMonth = prevMonth;
            currentYear = prevYear;
            loadCalendar(currentMonth, currentYear);
        }
    });

    $('#next-month').click(function() {
        let nextMonth = currentMonth + 1;
        let nextYear = currentYear;
        if (nextMonth > 11) {
            nextMonth = 0;
            nextYear++;
        }
        let formattedMonth = `${nextYear}-${String(nextMonth + 1).padStart(2, '0')}`;
        if (availableMonths.includes(formattedMonth)) {
            currentMonth = nextMonth;
            currentYear = nextYear;
            loadCalendar(currentMonth, currentYear);
        }
    });

    loadAvailableMonths();
});
