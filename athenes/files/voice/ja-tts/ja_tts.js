// IMPLEMENTED (X) or MISSING ( ) FEATURES, (N/A) if not needed in this language:
//
// (X) Basic navigation prompts: route (re)calculated (with distance and time support), turns, roundabouts, u-turns, straight/follow, arrival
// (X) Announce nearby point names (destination / intermediate / GPX waypoint / favorites / POI)
// (X) Attention prompts: SPEED_CAMERA; SPEED_LIMIT; BORDER_CONTROL; RAILWAY; TRAFFIC_CALMING; TOLL_BOOTH; STOP; PEDESTRIAN; MAXIMUM; TUNNEL
// (X) Other prompts: gps lost, off route, back to route
// (X) Street name and prepositions (onto / on / to) and street destination (toward) support
// (X) Distance unit support (meters / feet / yard)
// (N/A) Special grammar: (please specify which)
// (X) Support announcing highway exits

var metricConst;
var dictionary = {};
var tts;

//// STRINGS
////////////////////////////////////////////////////////////////
function populateDictionary(tts) {
	// ROUTE CALCULATED
	dictionary["route_is"] = tts ? tts ? "目的地まで" : "route_is.ogg" : "route_is.ogg";
	dictionary["route_calculate"] = tts ? "ルートを更新しました" : "route_calculate.ogg";
	dictionary["distance"] = tts ? "距離は" : "distance.ogg";

	// LEFT/RIGHT
	//dictionary["prepare"] = "Prepare to "
	dictionary["after"] = tts ? "先" : "after.ogg";
	dictionary["in"] = tts ? "先" : "in.ogg";

	dictionary["left"] = tts ? "左方向です。" : "left.ogg";
	dictionary["left_sh"] = tts ? "手前左方向です。" : "left_sh.ogg";
	dictionary["left_sl"] = tts ? "斜め左方向です。" : "left_sl.ogg";
	dictionary["right"] = tts ? "右方向です。" : "right.ogg";
	dictionary["right_sh"] = tts ? "手前右方向です。" : "right_sh.ogg";
	dictionary["right_sl"] = tts ? "斜め右方向です。" : "right_sl.ogg";
	// Note: "left_keep"/"right_keep" is a turn type aiding lane selection, while "left_bear"/"right_bear" is as brief "then..." preparation for the turn-after-next. In some languages l/r_keep may not differ from l/r_bear.
	dictionary["left_keep"] = tts ? "分岐を左方向です。" : "left_keep.ogg";
	dictionary["right_keep"] = tts ? "分岐を右方向です。" : "right_keep.ogg";
	dictionary["left_bear"] = tts ? "左方向です。" : "left_bear.ogg";    // in English the same as left_keep, may be different in other languages
	dictionary["right_bear"] = tts ? "右方向です。" : "right_bear.ogg";  // in English the same as right_keep, may be different in other languages

	// U-TURNS
	dictionary["make_uturn"] = tts ? "Uターンをして下さい。" : "make_uturn.ogg";
	dictionary["make_uturn_wp"] = tts ? "可能ならUターンをして下さい" : "make_uturn_wp.ogg";

	// ROUNDABOUTS
	dictionary["prepare_roundabout"] = tts ? "ロータリーがあります。" : "prepare_roundabout.ogg";
	//dictionary["roundabout"] = tts ? "enter the roundabout" : "roundabout.ogg";
	dictionary["then"] = tts ? "その先" : "then.ogg";
	//dictionary["and"] = tts ? "その先" : "and.ogg";
	dictionary["take"] = tts ? "ロータリの" : "take.ogg";
	dictionary["exit"] = tts ? "の出口です。" : "exit.ogg";

	dictionary["1st"] = tts ? "いち番目" : "1st.ogg";
	dictionary["2nd"] = tts ? "に番目" : "2nd.ogg";
	dictionary["3rd"] = tts ? "さん番目" : "3rd.ogg";
	dictionary["4th"] = tts ? "よん番目" : "4th.ogg";
	dictionary["5th"] = tts ? "ご番目" : "5th.ogg";
	dictionary["6th"] = tts ? "ろく番目" : "6th.ogg";
	dictionary["7th"] = tts ? "なな番目" : "7th.ogg";
	dictionary["8th"] = tts ? "はち番目" : "8th.ogg";
	dictionary["9th"] = tts ? "きゅう番目" : "9th.ogg";
	dictionary["10th"] = tts ? "じゅう番目" : "10th.ogg";
	dictionary["11th"] = tts ? "じゅういち番目" : "11th.ogg";
	dictionary["12th"] = tts ? "じゅうに番目" : "12th.ogg";
	dictionary["13th"] = tts ? "じゅうさん番目" : "13th.ogg";
	dictionary["14th"] = tts ? "じゅうよん番目" : "14th.ogg";
	dictionary["15th"] = tts ? "じゅうご番目" : "15th.ogg";
	dictionary["16th"] = tts ? "じゅうろく番目" : "16th.ogg";
	dictionary["17th"] = tts ? "じゅうなな番目" : "17th.ogg";

	// STRAIGHT/FOLLOW
	dictionary["go_ahead"] = tts ? "道なりに" : "go_ahead.ogg";
	dictionary["follow"] = tts ? "道なりに" : "follow.ogg";  // "Follow the course of the road for" perceived as too chatty by many users

	// ARRIVE
	dictionary["and_arrive_destination"] = tts ? "目的地です。" : "and_arrive_destination.ogg";
	dictionary["reached_destination"] = tts ? "目的地です。" : "reached_destination.ogg";
	dictionary["and_arrive_intermediate"] = tts ? "途中の目的地です。" : "and_arrive_intermediate.ogg";
	dictionary["reached_intermediate"] = tts ? "途中の目的地です。" : "reached_intermediate.ogg";

	// NEARBY POINTS
	dictionary["and_arrive_waypoint"] = tts ? "ウェイポイントです。" : "and_arrive_waypoint.ogg";
	dictionary["reached_waypoint"] = tts ? "ウェイポイントです。" : "reached_waypoint.ogg";
	dictionary["and_arrive_favorite"] = tts ? "お気に入り場所です。 " : "and_arrive_favorite.ogg";
	dictionary["reached_favorite"] = tts ? "お気に入り場所です。 " : "reached_favorite.ogg";
	dictionary["and_arrive_poi"] = tts ? "and pass POI" : "and_arrive_poi.ogg";
	dictionary["reached_poi"] = tts ? "you are passing POI" : "reached_poi.ogg";

	// ATTENTION
	//dictionary["exceed_limit"] = "you are exceeding the speed limit"
	dictionary["exceed_limit"] = tts ? "最高速度" : "exceed_limit.ogg";
	dictionary["attention"] = tts ? "ご注意下さい" : "attention.ogg";
	dictionary["speed_camera"] = tts ? "スピードカメラ" : "speed_camera.ogg";
	dictionary["border_control"] = tts ? "税関" : "border_control.ogg";
	dictionary["railroad_crossing"] = tts ? "踏切" : "railroad_crossing.ogg";
	dictionary["traffic_calming"] = tts ? "交通静穏化" : "traffic_calming.ogg";
	dictionary["toll_booth"] = tts ? "料金所" : "toll_booth.ogg";
	dictionary["stop"] = tts ? "一時停止標識" : "stop.ogg";
	dictionary["pedestrian_crosswalk"] = tts ? "横断歩道" : "pedestrian_crosswalk.ogg";
	dictionary["tunnel"] = tts ? "トンネル" : "tunnel.ogg";

	// OTHER PROMPTS
	dictionary["location_lost"] = tts ? "GPS信号を失いました。" : "location_lost.ogg";
	dictionary["location_recovered"] = tts ? "GPS信号が回復しました。" : "location_recovered.ogg";
	dictionary["off_route"] = tts ? "ルートから外れました。" : "off_route.ogg";
	dictionary["back_on_route"] = tts ? "ルートに復帰しました。" : "back_on_route.ogg";

	// STREET NAME PREPOSITIONS
	dictionary["onto"] = tts ? "に" : "onto.ogg";
	dictionary["on"] = tts ? "に" : "on.ogg";    // is used if you turn together with your current street, i.e. street name does not change.
	dictionary["to"] = tts ? "方面" : "to.ogg";
	dictionary["toward"] = tts ? "方面" : "toward.ogg";

	// DISTANCE UNIT SUPPORT
	dictionary["meters"] = tts ? "メートル" : "meters.ogg";
	dictionary["around_1_kilometer"] = tts ? "およそ1キロ" : "around_1_kilometer.ogg";
	dictionary["around"] = tts ? "およそ" : "around.ogg";
	dictionary["kilometers"] = tts ? "キロ" : "kilometers.ogg";

	dictionary["feet"] = tts ? "フィート" : "feet.ogg";
	dictionary["1_tenth_of_a_mile"] = tts ? "one tenth of a mile" : "1_tenth_of_a_mile.ogg";
	dictionary["tenths_of_a_mile"] = tts ? "tenths of a mile" : "tenths_of_a_mile.ogg";
	dictionary["around_1_mile"] = tts ? "about 1 mile" : "around_1_mile.ogg";
	dictionary["miles"] = tts ? "miles" : "miles.ogg";
	dictionary["yards"] = tts ? "yards" : "yards.ogg";

	// TIME SUPPORT
	dictionary["time"] = tts ? "時間" : "jikan.ogg";
	//dictionary["1_hour"] = tts ? "one hour " : "1_hour.ogg";
    dictionary["hours"] = tts ? "時間" : "jikan.ogg";
	dictionary["less_a_minute"] = tts ? "1分以内" : "ippun_inai.ogg";
	dictionary["1_minute"] = tts ? "1分" : "ippun.ogg";
    dictionary["2_minutes"] = tts ? "2分" : "ni_fun.ogg";
    dictionary["3_minutes"] = tts ? "3分" : "san_pun.ogg";
    dictionary["4_minutes"] = tts ? "4分" : "yon_pun.ogg";
    dictionary["5_minutes"] = tts ? "5分" : "go_fun.ogg";
    dictionary["6_minutes"] = tts ? "6分" : "roppun.ogg";
    dictionary["7_minutes"] = tts ? "7分" : "nana_fun.ogg";
    dictionary["8_minutes"] = tts ? "8分" : "happun.ogg";
    dictionary["9_minutes"] = tts ? "9分" : "kyuu_fun.ogg";
    dictionary["10_minutes"] = tts ? "10分" : "juppun.ogg";
	dictionary["minutes"] = tts ? "分" : "minutes.ogg";
}


//// COMMAND BUILDING / WORD ORDER
////////////////////////////////////////////////////////////////
function setMetricConst(metrics) {
	metricConst = metrics;
}

function setMode(mode) {
	tts = mode;
	populateDictionary(mode);
}

function route_new_calc(dist, timeVal) {
	return dictionary["route_is"] + " " + distance(dist) + " " + dictionary["time"] + " " + time(timeVal) + (tts ? ". " : " ");
}

function distance(dist) {
	switch (metricConst) {
		case "km-m":
			if (dist < 17 ) {
				return (tts ? Math.round(dist).toString() : ogg_dist(Math.round(dist))) + " " + dictionary["meters"];
			} else if (dist < 100) {
				return (tts ? (Math.round(dist/10.0)*10).toString() : ogg_dist(Math.round(dist/10.0)*10)) + " " + dictionary["meters"];
			} else if (dist < 1000) {
				return (tts ? (Math.round(2*dist/100.0)*50).toString() : ogg_dist(Math.round(2*dist/100.0)*50)) + " " + dictionary["meters"];
			} else if (dist < 1500) {
				return dictionary["around_1_kilometer"];
			} else if (dist < 10000) {
				return dictionary["around"] + " " + (tts ? Math.round(dist/1000.0).toString() : ogg_dist(Math.round(dist/1000.0))) + " " + dictionary["kilometers"];
			} else {
				return (tts ? Math.round(dist/1000.0).toString() : ogg_dist(Math.round(dist/1000.0))) + " " + dictionary["kilometers"];
			}
			break;
		case "mi-f":
			if (dist < 160) {
				return (tts ? (Math.round(2*dist/100.0/0.3048)*50).toString() : ogg_dist(Math.round(2*dist/100.0/0.3048)*50)) + " " + dictionary["feet"];
			} else if (dist < 241) {
				return dictionary["1_tenth_of_a_mile"];
			} else if (dist < 1529) {
				return (tts ? Math.round(dist/161.0).toString() : ogg_dist(Math.round(dist/161.0))) + " " + dictionary["tenths_of_a_mile"];
			} else if (dist < 2414) {
				return dictionary["around_1_mile"];
			} else if (dist < 16093) {
				return dictionary["around"] + " " + (tts ? Math.round(dist/1609.3).toString() : ogg_dist(Math.round(dist/1609.3))) + " " + dictionary["miles"];
			} else {
				return (tts ? Math.round(dist/1609.3).toString() : ogg_dist(Math.round(dist/1609.3))) + " " + dictionary["miles"];
			}
			break;
		case "mi-m":
			if (dist < 17) {
				return (tts ? Math.round(dist).toString() : ogg_dist(Math.round(dist))) + " " + dictionary["meters"];
			} else if (dist < 100) {
				return (tts ? (Math.round(dist/10.0)*10).toString() : ogg_dist(Math.round(dist/10.0)*10)) + " " + dictionary["meters"];
			} else if (dist < 1300) {
				return (tts ? (Math.round(2*dist/100.0)*50).toString() : ogg_dist(Math.round(2*dist/100.0)*50)) + " " + dictionary["meters"];
			} else if (dist < 2414) {
				return dictionary["around_1_mile"];
			} else if (dist < 16093) {
				return dictionary["around"] + " " + (tts ? Math.round(dist/1609.3).toString() : ogg_dist(Math.round(dist/1609.3))) + " " + dictionary["miles"];
			} else {
				return (tts ? Math.round(dist/1609.3).toString() : ogg_dist(Math.round(dist/1609.3))) + " " + dictionary["miles"];
			}
			break;
		case "mi-y":
			if (dist < 17) {
				return (tts ? Math.round(dist/0.9144).toString() : ogg_dist(Math.round(dist/0.9144))) + " " + dictionary["yards"];
			} else if (dist < 100) {
				return (tts ? (Math.round(dist/10.0/0.9144)*10).toString() : ogg_dist(Math.round(dist/10.0/0.9144)*10)) + " " + dictionary["yards"];
			} else if (dist < 1300) {
				return (tts ? (Math.round(2*dist/100.0/0.9144)*50).toString() : ogg_dist(Math.round(2*dist/100.0/0.9144)*50)) + " " + dictionary["yards"]; 
			} else if (dist < 2414) {
				return dictionary["around_1_mile"];
			} else if (dist < 16093) {
				return dictionary["around"] + " " + (tts ? Math.round(dist/1609.3).toString() : ogg_dist(Math.round(dist/1609.3))) + " " + dictionary["miles"];
			} else {
				return (tts ? Math.round(dist/1609.3).toString() : ogg_dist(Math.round(dist/1609.3))) + " " + dictionary["miles"];
			}
			break;
	}
}

function time(seconds) {
	var minutes = Math.round(seconds/60.0);
	if (seconds < 30) {
		return dictionary["less_a_minute"];
	} else if (minutes % 60 == 0 && tts) {
		return hours(minutes);
	} else if (tts) {
		return hours(minutes) + " " + (minutes % 60).toString() + " " + dictionary["minutes"];
	} else if (!tts && minutes % 60 > 0 && minutes % 60 < 11) {
		return hours(minutes) + " " + oggMinuteUnits(minutes);
	} else if (!tts && minutes % 60 > 11 ) {
        return hours(minutes) + " " + (Math.floor((minutes % 60)/10.0) * 10).toString() + ".ogg" + oggMinuteUnits(minutes % 60);
    } else if (!tts && (minutes % 60) % 10 == 0) {
		return hours(minutes) + " " + (Math.floor(minutes/10.0)).toString() + ".ogg" + dictionary["10_minutes"];
	}
    else if (!tts) {
		return hours(minutes);
	}
}

function oggMinuteUnits(minutes) {
    if (minutes % 60 == 1) {
		return dictionary["1_minute"];
	} else if (minutes % 60 == 2) {
		return dictionary["2_minutes"];
	} else if (minutes % 60 == 3) {
		return dictionary["3_minutes"];
	} else if (minutes % 60 == 4) {
		return dictionary["4_minutes"];
	} else if (minutes % 60 == 5) {
		return dictionary["5_minutes"];
	} else if (minutes % 60 == 6) {
		return dictionary["6_minutes"];
	} else if (minutes % 60 == 7) {
		return dictionary["7_minutes"];
	} else if (minutes % 60 == 8) {
		return dictionary["8_minutes"];
	} else if (minutes % 60 == 9) {
		return dictionary["9_minutes"];
	} else if (minutes % 60 == 10) {
		return dictionary["10_minutes"];
    }
}
function hours(minutes) {
	if (minutes < 60) {
		return "";
	} else {
		var hours = minutes / 60;
        return Math.floor(hours).toString() + (!tts ? ".ogg " : " ") + dictionary["hours"]; 
	}
}

function route_recalc(dist, seconds) {
	return dictionary["route_calculate"] + (tts ? ", " : " ") + dictionary["distance"] + " " + distance(dist) + " " + dictionary["time"] + " " + time(seconds) + ". ";
}

function go_ahead(dist, streetName) {
	if (dist == -1) {
		return dictionary["go_ahead"];
	} else {
		return dictionary["follow"] + " " + distance(dist) + " " + follow_street(streetName);
	}
}

function follow_street(streetName) {
	if ((streetName["toDest"] === "" && streetName["toStreetName"] === "" && streetName["toRef"] === "") || Object.keys(streetName).length == 0 || !tts) {
		return "";
	} else if (streetName["toStreetName"] === "" && streetName["toRef"] === "") {
		return dictionary["to"] + " " + streetName["toDest"];
	} else if (streetName["toRef"] === streetName["fromRef"] && streetName["toStreetName"] === streetName["fromStreetName"] || 
			(streetName["toRef"] == streetName["fromRef"] && streetName["toStreetName"] == "")) {
		return dictionary["on"] + " " + assemble_street_name(streetName);
	} else if (!(streetName["toRef"] === streetName["fromRef"] && streetName["toStreetName"] === streetName["fromStreetName"])) {
		return dictionary["to"] + " " + assemble_street_name(streetName);
	}
}

function turn(turnType, dist, streetName) {
	if (dist == -1) {
		return getTurnType(turnType) + " " + turn_street(streetName);
	} else {
		return distance(dist) + " " + dictionary["in"] + " " + getTurnType(turnType) + " " + turn_street(streetName); 
	}
}

function take_exit(turnType, dist, exitString, exitInt, streetName) {
	if (dist == -1) {
		return getTurnType(turnType) + " " + dictionary["onto"] + " " + getExitNumber(exitString, exitInt) + " " + take_exit_name(streetName)
	} else {
		return distance(dist) + " " + dictionary["in"] + " "
			+ getTurnType(turnType) + " " + dictionary["onto"] + " " + getExitNumber(exitString, exitInt) + " " + take_exit_name(streetName)
	}
}

function take_exit_name(streetName) {
	if (Object.keys(streetName).length == 0 || (streetName["toDest"] === "" && streetName["toStreetName"] === "") || !tts) {
		return "";
	} else if (streetName["toDest"] != "") {
		return (tts ? ", " : " ") + streetName["toStreetName"] + " " + dictionary["toward"] + " " + streetName["toDest"];
	} else if (streetName["toStreetName"] != "") {
		return (tts ? ", " : " ") + streetName["toStreetName"]
	} else {
		return "";
	}
}

function getExitNumber(exitString, exitInt) {
	if (!tts && exitInt > 0 && exitInt < 18) {
		return nth(exitInt) + " " + dictionary["exit"];
	} else if (tts) {
		return  dictionary["exit"] + " " + exitString;
	} else {
		return dictionary["exit"];
	}
}

function  getTurnType(turnType) {
	switch (turnType) {
		case "left":
			return dictionary["left"];
			break;
		case "left_sh":
			return dictionary["left_sh"];
			break;
		case "left_sl":
			return dictionary["left_sl"];
			break;
		case "right":
			return dictionary["right"];
			break;
		case "right_sh":
			return dictionary["right_sh"];
			break;
		case "right_sl":
			return dictionary["right_sl"];
			break;
		case "left_keep":
			return dictionary["left_keep"];
			break;
		case "right_keep":
			return dictionary["right_keep"];
			break;
	}
}

function then() {
	return " " + dictionary["then"] + " ";
}

function roundabout(dist, angle, exit, streetName) {
	if (dist == -1) {
		return dictionary["take"] + " " + nth(exit) + " " + dictionary["exit"] + " " + turn_street(streetName);
	} else {
		return distance(dist) + " " + dictionary["in"] +" " + dictionary["take"] + " " + nth(exit) + " " + dictionary["exit"] + " " + turn_street(streetName);
	}

}

function turn_street(streetName) {
	if (Object.keys(streetName).length == 0 || (streetName["toDest"] === "" && streetName["toStreetName"] === "" && streetName["toRef"] === "") || !tts) {
		return "";
	} else if (streetName["toStreetName"] === "" && streetName["toRef"] === "") {
		return streetName["toDest"] + " " + dictionary["toward"];
	} else if (streetName["toRef"] === streetName["fromRef"] && streetName["toStreetName"] === streetName["fromStreetName"]) {
		return assemble_street_name(streetName) + " " + dictionary["on"];
	} else if ((streetName["toRef"] === streetName["fromRef"] && streetName["toStreetName"] === streetName["fromStreetName"]) 
		|| (streetName["toStreetName"] === "" && streetName["toRef"] === streetName["fromRef"])) {
		return assemble_street_name(streetName) + " " + dictionary["on"];
	} else if (!(streetName["toRef"] === streetName["fromRef"] && streetName["toStreetName"] === streetName["fromStreetName"])) {
		return assemble_street_name(streetName) + " " + dictionary["onto"];
	}
	return "";
}

function assemble_street_name(streetName) {
	if (streetName["toDest"] === "") {
		return streetName["toRef"] + " " + streetName["toStreetName"];
	} else if (streetName["toRef"] === "") {
		return streetName["toStreetName"] + " " + streetName["toDest"] + " " + dictionary["toward"];
	} else if (streetName["toRef"] != "") {
		return streetName["toRef"] + " " + streetName["toDest"] + " " + dictionary["toward"];
	}
}

function nth(exit) {
	switch (exit) {
		case (1):
			return dictionary["1st"];
		case (2):
			return dictionary["2nd"];
		case (3):
			return dictionary["3rd"];
		case (4):
			return dictionary["4th"];
		case (5):
			return dictionary["5th"];
		case (6):
			return dictionary["6th"];
		case (7):
			return dictionary["7th"];
		case (8):
			return dictionary["8th"];
		case (9):
			return dictionary["9th"];
		case (10):
			return dictionary["10th"];
		case (11):
			return dictionary["11th"];
		case (12):
			return dictionary["12th"];
		case (13):
			return dictionary["13th"];
		case (14):
			return dictionary["14th"];
		case (15):
			return dictionary["15th"];
		case (16):
			return dictionary["16th"];
		case (17):
			return dictionary["17th"];
	}
}

function make_ut(dist, streetName) {
	if (dist == -1) {
		return dictionary["make_uturn"] + " " + turn_street(streetName);
	} else {
		return distance(dist) + " " + dictionary["in"] + " " + dictionary["make_uturn"] + " " + turn_street(streetName);
	}
}

function bear_left(streetName) {
	return dictionary["left_bear"];
}

function bear_right(streetName) {
	return dictionary["right_bear"];
}

function prepare_make_ut(dist, streetName) {
	return distance(dist) + " " + dictionary["after"] + " " + dictionary["make_uturn"] + " " + turn_street(streetName);
}

function prepare_turn(turnType, dist, streetName) {
	return distance(dist) + " " + dictionary["after"] + " " + getTurnType(turnType) + " " + turn_street(streetName);
}

function prepare_roundabout(dist, exit, streetName) {
	return distance(dist) + " " + dictionary["after"] + " " + dictionary["prepare_roundabout"]; 
}

function and_arrive_destination(dest) {
	return dictionary["and_arrive_destination"] + " " + dest;
}

function and_arrive_intermediate(dest) {
	return dictionary["and_arrive_intermediate"] + " " + dest;
}

function and_arrive_waypoint(dest) {
	return dictionary["and_arrive_waypoint"] + " " + dest;
}

function and_arrive_favorite(dest) {
	return dictionary["and_arrive_favorite"] + " " + dest;
}

function and_arrive_poi(dest) {
	return dictionary["and_arrive_poi"] + " " + dest;
}

function reached_destination(dest) {
	return dictionary["reached_destination"] + " " + dest;
}

function reached_waypoint(dest) {
	return dictionary["reached_waypoint"] + " " + dest;
}

function reached_intermediate(dest) {
	return dictionary["reached_intermediate"] + " " + dest;
}

function reached_favorite(dest) {
	return dictionary["reached_favorite"] + " " + dest;
}

function reached_poi(dest) {
	return dictionary["reached_poi"] + " " + dest;
}

function location_lost() {
	return dictionary["location_lost"];
}

function location_recovered() {
	return dictionary["location_recovered"];
}

function off_route(dist) {
	return dictionary["off_route"] + " " + distance(dist);
}

function back_on_route() {
	return dictionary["back_on_route"];
}

function make_ut_wp() {
	return dictionary["make_uturn_wp"];
}

// TRAFFIC WARNINGS
function speed_alarm(maxSpeed, speed) {
	return dictionary["exceed_limit"] + " " + maxSpeed.toString();
}

function attention(type) {
	return dictionary["attention"] + " " + getAttentionString(type);
}

function getAttentionString(type) {
	switch (type) {
		case "SPEED_CAMERA":
			return dictionary["speed_camera"];
			break;
		case "SPEED_LIMIT":
			return "";
			break
		case "BORDER_CONTROL":
			return dictionary["border_control"];
			break;
		case "RAILWAY":
			return dictionary["railroad_crossing"];
			break;
		case "TRAFFIC_CALMING":
			return dictionary["traffic_calming"];
			break;
		case "TOLL_BOOTH":
			return dictionary["toll_booth"];
			break;
		case "STOP":
			return dictionary["stop"];
			break;
		case "PEDESTRIAN":
			return dictionary["pedestrian_crosswalk"];
			break;
		case "MAXIMUM":
			return "";
			break;
		case "TUNNEL":
			return dictionary["tunnel"];
			break;
		default:
			return "";
			break;
	}
}

// DISTANCE MEASURE
function ogg_dist(distance) {
	if (distance == 0) {
		return "";
	} else if (distance < 20) {
		return Math.floor(distance).toString() + ".ogg ";
	} else if (distance < 1000 && (distance % 50) == 0) {
		return distance.toString() + ".ogg ";
	} else if (distance < 30) {
		return "20.ogg " + ogg_dist(distance - 20);
	} else if (distance < 40) {
		return "30.ogg " + ogg_dist(distance - 30);
	} else if (distance < 50) {
		return "40.ogg " + ogg_dist(distance - 40);
	} else if (distance < 60) {
		return "50.ogg " + ogg_dist(distance - 50);
	} else if (distance < 70) {
		return "60.ogg " + ogg_dist(distance - 60);
	} else if (distance < 80) {
		return "70.ogg "+ ogg_dist(distance - 70);
	} else if (distance < 90) {
		return "80.ogg " + ogg_dist(distance - 80);
	} else if (distance < 100) {
		return "90.ogg " + ogg_dist(distance - 90);
	} else if (distance < 200) {
		return "100.ogg " + ogg_dist(distance - 100);
	} else if (distance < 300) {
		return "200.ogg " + ogg_dist(distance - 200);
	} else if (distance < 400) {
		return "300.ogg "+ ogg_dist(distance - 300);
	} else if (distance < 500) {
		return "400.ogg " + ogg_dist(distance - 400);
	} else if (distance < 600) {
		return "500.ogg " + ogg_dist(distance - 500);
	} else if (distance < 700) {
		return "600.ogg " + ogg_dist(distance - 600);
	} else if (distance < 800) {
		return "700.ogg " + ogg_dist(distance - 700);
	} else if (distance < 900) {
		return "800.ogg " + ogg_dist(distance - 800);
	} else if (distance < 1000) {
		return "900.ogg " + ogg_dist(distance - 900);
	} else {
		return ogg_dist(distance/1000) + "1000.ogg " + ogg_dist(distance % 1000);
	}
}
