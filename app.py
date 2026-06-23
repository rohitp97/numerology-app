from flask import Flask, render_template, request, jsonify, make_response
from datetime import date
import io

from numerology import calculate_all

app = Flask(__name__)

# ── Content databases ──────────────────────────────────────────────────────────

MULANK_DATA = {
    1: {"title": "Mulank 1 — Sun", "text": "Born leader, radiates confidence, ambitious, bold, straightforward. Centre of attraction. Freedom lover. Avoid ego and overconfidence.", "favourable": "Mar 21 – Aug 20", "unfavourable": "Oct 15 – Dec 25", "lucky_color": "Red"},
    2: {"title": "Mulank 2 — Moon", "text": "Sensitive, intuitive, emotional, diplomatic. Natural peacemaker. Highly imaginative. Can be indecisive and overly sensitive.", "favourable": "Jul 20 – Aug 20", "unfavourable": "Oct 15 – Nov 14", "lucky_color": "White, Silver, Cream"},
    3: {"title": "Mulank 3 — Jupiter", "text": "Extremely ambitious, self-motivated, social, cheerful, religious. Great communicator and multitasker. Can be bossy.", "favourable": "Mid Feb – Mid Mar and Nov 25 – Dec 25", "unfavourable": "Oct – Nov", "lucky_color": "Yellow, Golden"},
    4: {"title": "Mulank 4 — Rahu", "text": "Practical, hardworking, disciplined, unconventional thinker. Challenges existing norms. Can be stubborn and rigid.", "favourable": "Jun 21 – Aug 20", "unfavourable": "Jan 14 – Feb 14", "lucky_color": "Electric Blue, Grey"},
    5: {"title": "Mulank 5 — Mercury", "text": "Versatile, quick-witted, adaptable, loves freedom and travel. Excellent communicator. Can be restless and inconsistent.", "favourable": "Jun 21 – Aug 20, Sep 21 – Oct 20", "unfavourable": "Dec 25 – Jan 14", "lucky_color": "Green, Light Grey"},
    6: {"title": "Mulank 6 — Venus", "text": "Loving, caring, family-oriented, artistic, harmonious. Natural nurturer. Can be possessive and self-sacrificing.", "favourable": "Apr 20 – May 20", "unfavourable": "Oct 15 – Nov 14", "lucky_color": "Pink, Light Blue, White"},
    7: {"title": "Mulank 7 — Ketu", "text": "Spiritual, introspective, analytical, mysterious. Seeker of truth. Can be isolated and melancholic.", "favourable": "Jul 20 – Sep 20", "unfavourable": "Dec 25 – Jan 14", "lucky_color": "Lavender, Violet"},
    8: {"title": "Mulank 8 — Saturn", "text": "Ambitious, disciplined, powerful, material-minded. Born for power and authority. Can be workaholic and ruthless.", "favourable": "Dec 25 – Jan 14", "unfavourable": "Mar 21 – Apr 20", "lucky_color": "Dark Blue, Black, Brown"},
    9: {"title": "Mulank 9 — Mars", "text": "Courageous, energetic, passionate, humanitarian. Natural warrior. Can be aggressive and impulsive.", "favourable": "Mar 21 – Apr 20", "unfavourable": "Oct 15 – Nov 14", "lucky_color": "Red, Crimson"},
}

MULANK_PDF_DATA = {
    1: "If you are born on the 1, 10, 19, or 28 of any month, your psychic number is 1 and you are ruled by the radiant Sun. Sun makes you a born leader, it makes your presence felt wherever you go and it wont be wrong to say that you are the life of the party. Oozing confidence comes naturally and easily to you. You have high self-esteem and are quite ambitious. You are bold and straightforward, and due to this people sometimes mistake you for being egoistic and arrogant, however, once they get to know you, they realize the warmth you have in your heart for the people around you and your kind spirit. Just like your psychic number, you wanna become number 1 in whatever you do and you also happen to become number 1 as you are stubborn in life, you are ready to burn the midnight oil and put in all your hard work to achieve your goals and dreams even at the cost of inconveniences and sacrifices.\n\nYour triumph and accomplishments are what keep you going and alive. You can take up leadership roles with ease in any sphere of your life and excel at it, be it your social circle, professional life, or personal. You are innovative and have a talent for using language in a charming, effective, and persuasive manner which attracts other people to you and they wish to listen to you. This is the reason why your friends and acquaintances come to you to seek advice. This boosts and motivates you and you also enjoy helping others. It gives you a sense of pride and keeps you propelled. As you are ruled by the Sun which is considered to be the King in Numerology, you desire to live a royal lifestyle and with your efforts and uphill battle, you are also able to achieve it. You love spending money and you spend it extravagantly to attain the luxuries and lavish lifestyle you wish and desire in life. Advice for you would be to keep a check on your savings and finances and not go over budget to achieve materialistic possessions.\n\nYou are always concerned and conscious about your public presence and your image. You enjoy being the centre of attraction just like your ruling planet, the Sun. You are known to carry a charismatic aura and a strong presence which attracts people toward you and creates curiosity in people to get to know you more. People around really enjoy spending time in your company and engaging in conversations with you. You do not like to be dominated or told what to do as you want to live your life and do your things on your terms. In other words, you are a freedom lover and dislike intrusions and interventions in your life and your style of working. You believe in being your own Boss.\n\nSome things that you must keep in mind to avoid discord and disturbances are to not dictate to others or to let your authoritative nature overpower your relationship with others, especially with your family members and friends. You possess a great deal of confidence which is phenomenal but do not let your overconfidence and ego drive your life in the wrong direction and cause distress and disagreements in your life. You indeed find it difficult to change your perception and opinion, but you must try to understand the perspective of others rather than imposing your thought process and ideologies on them. It is also seen that you tend to become discouraged and downhearted when you do not achieve what you desire, you are advised to accept delays and failures as it is all a part of life, a single event cannot decide your fate but a single failure can add a whole lot of experience to your life and put you on the path to success.\n\nFavourable Period: The most favourable time for you is the period between March 21st to August 20th as your birth date ruler, the Sun, is at its strongest and the most active during this season. This time yields prosperous and promising results. You must make optimum use of this period and choose it to start a new venture, make new investments, make new plans and goals, and start an auspicious activity, task, or project.\n\nUnfavourable Period: You must avoid starting any new and important activity from October 15th to December 25th as the Sun is weak during that phase. This term might bring some unwelcoming experiences such as a lack of motivation, procrastination, distractions, delays, stress, health issues, financial losses, unnecessary worries, and false allegations which could lead to defamation.\n\nLucky Colours: Red and shades of red are auspicious for you. You must include them in your daily life and surround yourself with these colours to attract luck. You may wear clothes or accessories associated with that colour, add this colour to your home decor, use red bed sheets, covers, and towels, use a red coloured phone cover, or change your phone lock screen and home screen to red wallpapers.",

    2: "If you are born on the 2nd, 11th, 20th, or 29th of any month, your psychic number is 2 and you are ruled by the gentle Moon. The Moon makes you highly sensitive, intuitive, and emotionally aware. You are a natural peacemaker and diplomat who instinctively understands the feelings of others. Your empathy and compassion draw people to you, and you are often the person others turn to in times of need. You have a rich inner life and a vivid imagination that can be a tremendous creative asset.\n\nYou are naturally cooperative and prefer to work in harmony with others rather than in competition. You thrive in partnerships and collaborations, and your ability to understand multiple perspectives makes you an excellent mediator and counselor. You possess a deep love for beauty, music, and the arts, and you appreciate the finer things in life. Your home is your sanctuary, and you invest great care in creating a warm and welcoming environment for your loved ones.\n\nOne of your greatest gifts is your intuition. You often sense things before they happen, and your gut feelings are remarkably accurate. Learning to trust this inner voice is one of your most important life lessons. However, your sensitivity can also be a vulnerability, as you are easily affected by the emotions and moods of those around you. Developing emotional boundaries will help you maintain your own wellbeing while continuing to support others.\n\nYou can sometimes struggle with indecision, as you are able to see all sides of a situation and find it difficult to commit to one course of action. Learning to make decisions with confidence while honoring your sensitivity is a key growth area for you. You also have a tendency toward self-doubt, and it is important for you to develop self-confidence and trust in your own abilities and judgements.\n\nFavourable Period: The most favourable time for you is between July 20th and August 20th, when the Moon and its energy are most active and supportive. This is an excellent time to begin new ventures, deepen relationships, and pursue creative projects. Make the most of this period for important decisions and new beginnings.\n\nUnfavourable Period: The period between October 15th and November 14th can bring emotional turbulence, indecision, and misunderstandings. Avoid making major decisions during this time and focus instead on introspection and emotional healing.\n\nLucky Colours: White, Silver, and Cream are your most auspicious colours. Wearing or surrounding yourself with these colours can enhance your intuition, bring calm to your emotions, and attract positive energy into your life. Consider using white or silver tones in your home decor, clothing, and accessories.",

    3: "If you are born on the 3rd, 12th, 21st, or 30th of any month, your psychic number is 3 and your ruling planet is Jupiter.\n\nYou are known to be extremely ambitious, by your very own will, and are self-motivated. It wont be wrong to say that hard work gives you pleasure. If you do not work hard, you feel something is missing or as if you are not giving it your 100 per cent. You thrive for bigger things and accomplishments in your professional life and cannot see yourself settling for subordinate positions.\n\nYou want to achieve one thing after the other, and you also make it happen given your devotion, discipline, and commitment to your work. Your dedication is a result of not wanting to see struggles in your life that you might have had to face in your early professional years. Psychic number 3 individuals start their careers early and might have to face hardship during that time which sets them up for success in the future. In reality, it shapes you to face any obstacle and learn how to overcome situations and come out as a winner.\n\nYou learn how to deal with people around you and how to handle situations. You just dont have time to work but also to play. You are social and cheerful and like to engage in conversations with people. You are also known to have a good sense of humour.\n\nYou are religious and have faith in God or the Supreme Power, you may or may not show it to the world but in your heart, you believe in cosmic energy. You like to express yourself with gestures, light humoured jokes and love the attention you get because of it. It would be correct to say you like to be in the spotlight and be the centre of attraction for all good reasons which are, your efforts and your endeavours.\n\nYou are valued for your optimism and for how well you can manage everything. You maintain your personal life equally enjoyable and vivid, however, it is seen that sometimes you find it difficult to draw the line between personal and professional lives which in turn disturbs your work-life balance.\n\nYou can multitask and are great at it. You can perform, manage, and organize several tasks, meetings, responsibilities, and home duties at the same time but your inclination from time to time is more towards your professional life than your personal life.\n\nIn your personal life, you are an extremely caring and loving individual who wants to provide for their family and loved ones. In relationships, you give all you possibly can to make your partner feel loved and secure, however, sometimes your partner will also have to experience your bossy and dictatorial nature.\n\nFavourable Period: The most favourable and beneficial times for you are the periods between Mid February to Mid March and November 25th to December 25th. You must make optimum use of this period to start a new venture, make new investments, create new plans, set your goals, and start an auspicious activity. This period results in being very beneficial for travelling.\n\nUnfavourable Period: You must avoid starting any new and important activities during October and November as they may bring dissatisfactory results. This period is also unfavourable for travelling.\n\nLucky Colours: Yellow, Golden, and shades of yellow and golden are auspicious for you. You must include them in your daily life and surround yourself with these colours to attract luck.",

    4: "If you are born on the 4th, 13th, or 22nd of any month, your psychic number is 4 and you are ruled by the shadow planet Rahu. Rahu makes you unconventional, original, and a challenger of established norms and conventions. You see the world differently from most people and often arrive at solutions and ideas that others overlook. You are practical and hardworking, and once you set your mind to something, you pursue it with tremendous discipline and dedication.\n\nYou possess a powerful intellect and a strong sense of logic. You are methodical in your thinking and prefer to have a solid plan before taking action. Your pragmatic nature means you excel at turning ideas into tangible realities. You are the kind of person who builds things that last, whether in your professional life, your relationships, or your personal projects. People often come to rely on you precisely because of your dependability and your thoroughness.\n\nRahu's influence can create a sense of restlessness and dissatisfaction in you. You may sometimes feel like an outsider or that your unconventional views are not appreciated or understood by those around you. This can lead to feelings of isolation or frustration. However, it is precisely your different perspective that is your greatest gift to the world, and over time, others will come to recognize and value the originality of your thinking.\n\nYou may find that your plans are frequently disrupted or that just when things seem to be going well, an unexpected change of direction occurs. This is a hallmark of Rahu's influence. Learning to embrace change and to adapt your plans without losing sight of your goals is one of the most important lessons for you. Developing focus and learning to direct your energy in a sustained manner will bring you tremendous rewards.\n\nFavourable Period: The period between June 21st and August 20th is your most favourable time. During this period, your efforts are more likely to bear fruit, and new opportunities are more likely to manifest. Take advantage of this window to launch new projects, form important partnerships, and make significant decisions.\n\nUnfavourable Period: The period between January 14th and February 14th may bring challenges, obstacles, and a sense that progress is stalled. Avoid starting new ventures during this time and focus on consolidating existing work and completing ongoing projects.\n\nLucky Colours: Electric Blue and Grey are your most auspicious colours. Incorporating these shades into your wardrobe, accessories, and living space can help you harness Rahu's positive energy while grounding your unconventional ideas in practical reality.",

    5: "If you are born on the 5th, 14th, or 23rd of any month, your psychic number is 5 and you are ruled by the planet Mercury. Mercury bestows upon you a quick mind, excellent communication skills, and an insatiable curiosity about the world around you. You are versatile, adaptable, and thrive on variety and stimulation. You are the kind of person who can effortlessly move between different social circles, topics, and activities, and you rarely stay in one place or one state of mind for long.\n\nYou possess a natural gift for communication in all its forms, whether it is writing, speaking, negotiating, or simply engaging in conversation. People enjoy your company because you bring energy, wit, and fresh perspectives to every interaction. You are quick-witted and have a wonderful sense of humor that can lighten any situation. Your ability to think on your feet and adapt to changing circumstances is one of your most valuable assets in both your personal and professional life.\n\nYou have a deep love of freedom and independence and resist anything that feels confining or restrictive. Travel, new experiences, and learning are among your greatest joys. You are drawn to people and ideas that are different from what you already know, and you are constantly adding to your storehouse of knowledge and experience. This adventurous spirit keeps you young at heart and ensures that life rarely becomes dull or routine.\n\nOne of the challenges you may face is a tendency toward restlessness and inconsistency. You may find it difficult to stick with one thing long enough to master it fully, or you may start many projects without completing them. Developing discipline and the ability to focus your considerable energy will be one of your most important growth areas. Learning to channel your natural versatility into sustained effort will allow you to achieve truly remarkable results.\n\nFavourable Period: Your most favourable periods are June 21st to August 20th and September 21st to October 20th. During these times, Mercury's influence is strongest and most supportive, making them ideal for communication, negotiations, travel, learning, and launching new ventures.\n\nUnfavourable Period: The period between December 25th and January 14th may bring miscommunications, travel delays, and a scattering of energy. Avoid signing important contracts or making major commitments during this time, and focus on review and reflection rather than new initiatives.\n\nLucky Colours: Green and Light Grey are your most auspicious colours. Green, in particular, resonates with Mercury's energy and can help sharpen your intellect, improve your communication, and attract good fortune. Include these colours in your daily life through clothing, accessories, and your living environment.",

    6: "If you are born on the 6th, 15th, or 24th of any month, your psychic number is 6 and you are ruled by the beautiful planet Venus. Venus blesses you with a deep love of beauty, harmony, and the finer things in life. You are naturally charming, warm, and magnetic, and people are drawn to your gentle yet radiant presence. You have a strong aesthetic sense and a talent for creating beautiful environments and experiences for those around you.\n\nYou are a natural nurturer and caregiver, and your family and loved ones are of paramount importance to you. You invest deeply in your relationships and give freely of your time, energy, and love. Your home is your pride and joy, and you work hard to make it a haven of comfort and beauty. You have a strong sense of responsibility and take your duties to others seriously, sometimes to the point of placing their needs ahead of your own.\n\nYou possess artistic talents and an appreciation for music, art, and culture. Whether or not you pursue a formal creative career, bringing beauty into the world in some form is a deep calling for you. You have an eye for aesthetics and a gift for harmony, and these qualities enrich every area of your life. People often turn to you for advice on matters of taste, relationships, and how to create more beauty and balance in their own lives.\n\nOne of the challenges for you is a tendency toward possessiveness and a difficulty letting go, whether in relationships, situations, or material things. Learning to love with an open hand and to trust that what is truly yours will remain with you is one of your most important life lessons. You may also have a tendency toward self-sacrifice that can lead to resentment over time. Developing healthy boundaries and learning to receive as graciously as you give will bring greater balance and fulfillment.\n\nFavourable Period: Your most favourable period is April 20th to May 20th, when Venus's energy is at its most potent. This is an ideal time for romantic matters, creative projects, financial decisions, and anything to do with beauty, art, or relationships. Make the most of this window for important new beginnings.\n\nUnfavourable Period: October 15th to November 14th can bring challenges in relationships, financial matters, and creative endeavors. Focus on maintaining existing commitments during this period rather than initiating new ones.\n\nLucky Colours: Pink, Light Blue, and White are your most auspicious colours. These shades resonate beautifully with Venus's energy and can help attract love, creativity, and harmony into your life. Wear them, decorate with them, and surround yourself with them as often as possible.",

    7: "If you are born on the 7th, 16th, or 25th of any month, your psychic number is 7 and you are ruled by the mystical shadow planet Ketu. Ketu bestows upon you a deep spiritual nature, a powerful intuition, and a profound wisdom that often sets you apart from those around you. You are a natural seeker of truth and meaning, and you are rarely satisfied with surface-level explanations or shallow experiences. You have a penetrating mind that delves beneath appearances to find deeper truths.\n\nYou are highly introspective and need regular periods of solitude and quiet reflection to process your experiences and reconnect with your inner wisdom. You are deeply philosophical by nature and are drawn to the great questions of life, spirituality, and existence. Many people with psychic number 7 find themselves drawn to meditation, philosophy, metaphysical studies, or other practices that help them explore the deeper dimensions of reality.\n\nYou possess excellent analytical and research abilities and can focus on a subject with remarkable concentration and depth. You are thorough and methodical in your thinking and tend to arrive at highly original insights and conclusions. Your mind works best when it is given time to go deep rather than wide, and your best work often comes from sustained periods of focused study and reflection. You may seem quiet or reserved to others, but beneath this exterior lies a rich inner world that is constantly alive with insight and intuition.\n\nYour challenge is to share your gifts and insights with others rather than keeping them to yourself. There can be a tendency toward isolation or a preference for the inner world over the outer one, and developing the ability to communicate your wisdom to others is one of your most important growth areas. You may also at times feel melancholy or struggle with feelings of being misunderstood. Learning to connect with others who share your depth and to find communities that value your kind of intelligence will bring you much greater joy.\n\nFavourable Period: Your most favourable period is July 20th to September 20th, when Ketu's energy is most supportive of your deeper nature. This is an excellent time for spiritual practices, research, study, and any projects requiring deep thought and analysis. Important insights and breakthroughs are more likely to occur during this period.\n\nUnfavourable Period: December 25th to January 14th may bring a sense of confusion, withdrawal, or lack of direction. Avoid major decisions during this time and focus on inner work, meditation, and self-care.\n\nLucky Colours: Lavender and Violet are your most auspicious colours. These spiritual shades resonate with Ketu's otherworldly energy and can help deepen your intuition, enhance your spiritual awareness, and bring clarity to your thoughts. Use them in your clothing, accessories, and living environment.",

    8: "If you are born on the 8th, 17th, or 26th of any month, your psychic number is 8 and you are ruled by the powerful planet Saturn. Saturn is the planet of karma, discipline, and hard work, and its influence makes you one of the most ambitious, determined, and capable individuals in all of numerology. You are built for success and for positions of authority and power. You understand intuitively that great achievements require great effort, and you are willing to pay the price.\n\nYou possess exceptional organizational abilities, a strong sense of discipline, and an executive mind that is capable of managing complex systems, projects, and people. You have a natural authority and gravitas that others respect, and you often find yourself in positions of leadership and responsibility, whether you sought them out or not. You are not afraid of hard work or of the challenges and obstacles that life puts in your path. In fact, you often perform best when faced with adversity, which has the effect of sharpening your focus and bringing out your formidable reserves of determination.\n\nSaturn's influence also gives you a deep connection to karmic principles. You understand that actions have consequences and that what you put out into the world will return to you. This wisdom, when fully internalized, makes you a person of great integrity and ethical strength. You are also deeply concerned with building something lasting and substantial, whether in your career, your financial life, or your contribution to society. Legacy matters deeply to you.\n\nOne of the significant challenges for those with psychic number 8 is the tendency to become so absorbed in work and material achievement that personal relationships and health are neglected. Saturn can also bring a certain heaviness or seriousness to your personality that can make it difficult to relax and enjoy the lighter aspects of life. Learning to balance your tremendous drive for achievement with joy, play, and nurturing connection with others is one of the most important lessons for you.\n\nFavourable Period: Your most favourable period is December 25th to January 14th, when Saturn's energy is at its peak. This is an excellent time to make important career decisions, launch business ventures, set long-term financial goals, and consolidate your position and resources.\n\nUnfavourable Period: March 21st to April 20th may bring obstacles, conflicts with authority, or setbacks in your plans. It is wise to avoid major confrontations or bold new initiatives during this period and to focus instead on patient, steady progress.\n\nLucky Colours: Dark Blue, Black, and Brown are your most auspicious colours. These earthy, powerful shades resonate with Saturn's energy and can help you project authority, attract material success, and maintain focus on your long-term goals.",

    9: "If you are born on the 9th, 18th, or 27th of any month, your psychic number is 9 and you are ruled by the dynamic and energetic planet Mars. Mars bestows upon you tremendous courage, energy, passion, and drive. You are a natural warrior and fighter who approaches life with boldness and intensity. You are not the kind of person who sits on the sidelines while life passes by. You engage with the world fully and directly, bringing your considerable fire and determination to everything you do.\n\nYou have a deep humanitarian streak and a genuine concern for the wellbeing of others. You are often drawn to causes, movements, or professions where you can make a positive difference in the world and stand up for those who cannot stand up for themselves. Your passion and conviction are inspiring to others, and you have a natural ability to mobilize people and lead them toward a common goal. Whether in your professional life or your personal relationships, you bring tremendous energy, loyalty, and generosity to everything you commit to.\n\nYou possess natural leadership qualities and a directness of expression that people often find refreshing, though it can sometimes come across as blunt or even aggressive. You speak your mind without hesitation and have little patience for dishonesty, manipulation, or timewasting. Your standards are high, both for yourself and for those around you, and you can become frustrated or impatient when others do not match your level of commitment and effort. Learning to channel your intensity in constructive directions is one of your most important ongoing practices.\n\nOne of the challenges for psychic number 9 individuals is a tendency toward impulsiveness and a difficulty controlling anger when provoked. Mars's fiery energy needs healthy outlets, such as physical exercise, sports, or creative expression, to prevent it from turning into frustration or conflict. Developing patience and the ability to see situations from multiple perspectives will serve you enormously in your relationships and your career.\n\nFavourable Period: March 21st to April 20th is your most favourable period, when Mars's energy is at its most powerful and supportive. This is an excellent time to launch new ventures, take on challenging projects, assert yourself in important situations, and pursue your most ambitious goals.\n\nUnfavourable Period: October 15th to November 14th can bring conflict, frustration, and depletion of energy. Avoid confrontations and impulsive decisions during this period, and focus on conserving your energy and working steadily rather than forcing outcomes.\n\nLucky Colours: Red and Crimson are your most auspicious colours. These powerful, energetic shades resonate with Mars's fiery nature and can help amplify your confidence, courage, and natural leadership qualities. Wear them, use them in your home decor, and surround yourself with these colours to attract Mars's positive energy.",
}

BHAGYANK_DATA = {
    1: "Destiny of leadership and individuality. Blessed with originality and pioneering spirit. Must develop independence and avoid dependence on others. Success through self-effort.",
    2: "Destiny of harmony and cooperation. Natural diplomat and mediator. Success through partnerships and teamwork. Must avoid over-sensitivity and indecision.",
    3: "Destiny of creativity and self-expression. Blessed with communication skills and optimism. Success through creative pursuits and social connections. Avoid scattering energy.",
    4: "Mental power, practicality, reads between the lines. Plans often get disrupted. Fickle focus due to Rahu influence. Unconventional ideas that take time to be accepted. Rely on brain over brawn. Maintain focus for miracles.",
    5: "Destiny of freedom and change. Highly adaptable, loves travel and variety. Success through versatility and communication. Must develop discipline and consistency.",
    6: "Destiny of love and responsibility. Natural caretaker and harmonizer. Success through service to family and community. Must avoid martyrdom and possessiveness.",
    7: "Spirituality and intuition. Becomes everyone's favourite naturally. Healer by nature - talking to them comforts others. Wisdom and deep knowledge. Foreign recognition likely. If married before 28, marital issues possible. Drawn to occult sciences later in life.",
    8: "Destiny of power and material achievement. Must overcome obstacles to reach success. Karmic lessons around money and authority. Great potential for business and leadership.",
    9: "Destiny of humanitarian service. Strong idealism and compassion. Success through helping others and fighting for causes. Must channel aggression productively.",
}

BHAGYANK_PDF_DATA = {
    1: "It is ruled by the Sun.\n\nDestiny number 1 represents leadership, independence, and the pioneering spirit. You are destined to stand out, to lead, and to carve new paths that others will follow. The Sun's influence on your destiny number ensures that leadership and authority are natural themes throughout your life. From an early age, you likely found yourself taking charge of situations, whether formally or informally, and others naturally looked to you for direction and guidance.\n\nYou possess strong willpower, determination, and an innate drive to achieve and excel. You have original ideas and the confidence to pursue them even when others are skeptical. Your destiny is to develop your own unique identity and to follow your own path rather than conforming to the expectations of others. You do your best work when you have the freedom to operate independently and to make your own decisions.\n\nThe path of DN 1 brings you opportunities to lead in multiple spheres of your life, but it also brings the lesson of learning to balance leadership with humility. The greatest leaders know how to inspire and empower those around them rather than simply dominating. Learning to listen, to collaborate, and to acknowledge the contributions of others will be one of your most important ongoing growth areas.\n\nDN 1 individuals often experience significant new beginnings in their lives, whether in the form of new careers, relocations, relationships, or personal transformations. These new beginnings are often catalyzed by your own courage and initiative. You are the kind of person who makes things happen rather than waiting for life to happen to you, and this proactive quality is one of your greatest strengths.",

    2: "It is ruled by the Moon.\n\nDestiny number 2 represents cooperation, harmony, and the deep power of relationships. You are destined to be a bridge-builder, a mediator, and a creator of harmony in whatever sphere of life you inhabit. The Moon's influence on your destiny number gives you exceptional sensitivity to the emotional currents around you and a natural gift for understanding and supporting others. Your life path brings you into the realm of relationships, partnerships, and collaborative endeavors.\n\nYou have a powerful intuition that grows stronger as you age, and learning to trust and honor this inner knowing is one of your most important life lessons. The Moon's influence can make you highly sensitive to your environment, to other people's moods, and to subtle energies that others may not even notice. This sensitivity is both your greatest gift and one of your greatest challenges. It enables you to connect deeply with others, but it can also leave you feeling overwhelmed or drained if you do not develop healthy boundaries.\n\nDN 2 brings opportunities for deep and meaningful partnerships throughout your life, both professional and personal. Your greatest successes are likely to come through collaboration and cooperation rather than solo effort. You excel at supporting and enhancing the work of others, at finding common ground between opposing viewpoints, and at creating environments of trust and mutual understanding. Diplomacy and tact are among your most valuable tools.\n\nOne of the key lessons of DN 2 is learning to value your own needs and to assert yourself without losing your natural gentleness and consideration for others. You may have a tendency to put others first to such an extent that your own needs go unmet. Developing the confidence to advocate for yourself while maintaining your gracious and harmonious nature is one of the most important aspects of your destiny.",

    3: "It is ruled by Jupiter.\n\nDestiny number 3 represents creativity, self-expression, and the power of joyful communication. You are destined to share your gifts with the world through your words, your art, your ideas, and your irrepressible sense of joy and optimism. Jupiter's expansive and generous influence on your destiny number ensures that creativity and self-expression are central themes throughout your life. You are meant to inspire, uplift, and delight those around you.\n\nYou are blessed with a natural gift for communication and a charisma that draws others to you. Whether through writing, speaking, performing, or simply engaging in conversation, you have the ability to captivate and inspire your audience. You are naturally optimistic and have an infectious enthusiasm that lifts the spirits of those around you. People feel better for having spent time in your company, and this is one of the most precious gifts you bring to the world.\n\nJupiter's influence also brings a love of learning, travel, and philosophical exploration to your destiny. You are drawn to big ideas and to experiences that expand your understanding of life and the world. You have a natural generosity of spirit and enjoy sharing what you know and what you have with others. Teaching, mentoring, and guiding others may be important aspects of your life path, whether formally or informally.\n\nOne of the key challenges of DN 3 is learning to channel your expansive creative energy in a focused and disciplined way. You have so many ideas and interests that it can be difficult to commit fully to any one path. Developing the discipline to follow through on your creative projects and commitments will enable you to fully realize your considerable potential. The world needs what you have to offer, and it is worth the effort of bringing your gifts to full expression.",

    4: "It is ruled by the shadow planet Rahu.\n\nDestiny number 4 represents mental power, intellectual prowess, and practicality. You are clever and adept at reading between the lines. You highly likely comprehend the original motives and intentions of others by merely having a conversation with them. Its rather unfortunate that people often misunderstand you. You try to convey one thing, but they interpret it wrongly. This misunderstanding makes it utterly difficult to be in their good graces. This is the chief reason why you may find yourself ending up with only a handful of friends after a certain age, or find it hard to make friends. You are careful, proactive, and like to plan things ahead of time. You are practical and your pragmatic approach brings favorable results.\n\nRahu is a mischievous and dynamic planet that never likes to stay in one place. It shows its influence on various aspects of your life:\n- You would find yourself making big career plans for the future, but end up doing something entirely different.\n- You would feel something is always missing in life, you cannot put your finger on it, even when you have everything you need.\n- Rahu brings disappointment in at least one facet of your life.\n- Health issues become a concern as well.\n- Although you have the stamina to tackle physical work, your physical labour gets unnoticed. Rahu makes it almost certain that the output of brain activity is far superior and appreciated than the result of any physical activity.\n- As Rahu doesnt stay put, it affects your focus. You would find yourself most productive when focused, but your focus flutters frequently.\n- Rahu is known to be highly fickle and destroys masterplans. If you notice impedance and disruption in your plans, this is the reason.\n- You may miss out on opportunities because of your sceptical nature.\n- Unavoidable additional responsibilities and duties are likely to come your way.\n\nIn numerology, the number 4 also represents unconventional ways, revolutions, and challenging existing notions. The best way to get the most out of your destiny is:\n- The more you rely and utilize your brain over brawn, the faster you accomplish your goals.\n- Resort to criticism and bluntness only when required.\n- Maintain focus and do activities that enforce your focus. The results will be nothing short of a miracle.",

    5: "It is ruled by Mercury.\n\nDestiny number 5 represents freedom, versatility, and the transformative power of change and experience. You are destined to be an agent of change in your own life and in the lives of those around you. Mercury's quicksilver influence on your destiny number ensures that adaptability, communication, and the embrace of variety are central themes throughout your life journey. You thrive on movement, on new experiences, and on the stimulation of the unexpected.\n\nYou are destined to experience many different phases, environments, and roles throughout your life, and each of these experiences contributes to the richness and depth of your character. Your destiny is not one of sameness or routine but of constant evolution and discovery. This can be both exhilarating and challenging, as it requires you to remain flexible and open to change even when stability and predictability feel more comfortable.\n\nDN 5 brings opportunities for travel, learning, and the exploration of diverse cultures, ideas, and ways of life. Your best opportunities often come through unexpected channels, through chance meetings, sudden opportunities, or changes of direction that you did not plan. Learning to remain alert to these unexpected openings and to have the courage to seize them when they appear is one of the most important skills for you to develop.\n\nOne of the key lessons of DN 5 is learning to develop discipline and follow-through amid all the variety and change that defines your path. There can be a tendency to move on before things are fully completed, or to shy away from commitments that feel too restrictive. Finding the balance between your need for freedom and the stability and depth that come from genuine commitment will be one of the most rewarding aspects of your journey.",

    6: "It is ruled by Venus.\n\nDestiny number 6 represents love, responsibility, and the sacred calling of service to family and community. You are destined to be a nurturer, a harmonizer, and a creator of beauty in the world. Venus's gracious and loving influence on your destiny number ensures that relationships, beauty, and a deep sense of responsibility are central themes throughout your life. Your destiny is to give love freely and to create environments of harmony and care wherever you go.\n\nYou are destined to take on significant responsibilities in your life, often in the role of caregiver, provider, or protector. Whether through your family, your profession, or your community, you will find yourself called to serve and to support others. This is not a burden but a calling that, when embraced fully, brings you deep satisfaction and a profound sense of purpose. You are at your best when you are contributing to the wellbeing of others and when your environment reflects the beauty and harmony you carry within you.\n\nVenus's influence also makes you deeply attuned to aesthetics, art, and the beauty of the natural world. You may have significant artistic talent, or you may simply have a highly developed sense of beauty that expresses itself in the way you dress, decorate your home, or curate the experiences you share with others. Creating beauty is one of the ways you give love to the world, and this is a gift that should not be underestimated.\n\nOne of the key lessons of DN 6 is learning to set healthy boundaries and to avoid the trap of martyrdom. Your deep desire to give and to serve can sometimes lead you to give more than you have, leaving you depleted and resentful. Learning to receive as graciously as you give and to nurture yourself with the same love and care you offer to others will enable you to sustain your gifts and to serve from a place of genuine fullness rather than depletion.",

    7: "It is ruled by half-planet Ketu.\n\nDestiny number 7 represents spirituality and intuition.\n\nThe greatest attribute of DN 7 is its power to enhance the qualities of your Psychic Number manyfold. You would notice that you possess superior qualities of your Psychic Number than you would find in others with the same Psychic Number.\n\nDN 7 blesses you with the power of adaptability, hence you will find yourself easily adjusting to changing times and situations. You would find it natural to keep yourself in touch with the changing technologies and ideas and bring about these changes in yourself to remain abreast of the ever-changing world.\n\nYou are prompt in distinguishing a good trait in a person and accepting and blending it with your traits naturally. You would find that you end up becoming everyones favourite. It is due to DN 7 that enables you to organically understand others and their emotions.\n\nDN 7 highlights intuition. You would realize that as you enter your late twenties, you become highly intuitive and it lasts till you are well in your forties. You may develop a superior instinct for reading people. You would realize that you become very perceptive and understand people without them giving you much information.\n\nYou get your best ideas in your dreams and while daydreaming. Unlike others, who may be quick to reject such ideas, you take them constructively and are prompt to act on them.\n\nDestiny Number 7 also makes you a healer. By merely talking to you, others feel comforted. They seek out your company when they are distressed, dismayed, or dejected. You may not like the person or vice versa, but your advice is always for the betterment of that individual. With this healing power, you may pick out a career in the line of mental and physical healing.\n\nAs ruled by Destiny Number 7, you would find that you get confused easily. When in confusion, the first instinct could be to run away from the problem instead of tackling it. On the other hand, when pushed and encouraged by another person, you power through the situation.\n\n7 is also the number that denotes wisdom. It is right to say that you are a knowledgeable person and demonstrate your knowledge fluently and proficiently, making you a good orator and a brilliant narrator.\n\nDestiny Number 7 brings recognition in foreign countries. You may be showered with plenty of opportunities to work abroad and make a name for yourself.\n\nAs ruled by Destiny Number 7, marital and romantic relationship problems sometimes become inevitable. It has been seen that if people get married after 28, they are more likely to enjoy a successful marriage.\n\nIt is likely for you to develop a strong inclination toward spirituality and occult sciences at a later age. You would find it rather fascinating and end up doing exceedingly well if it is chosen as a career field.",

    8: "It is ruled by Saturn.\n\nDestiny number 8 represents power, material mastery, and the fulfillment of ambitious goals through sustained effort and integrity. You are destined to achieve significant material success and to exercise authority and influence in your professional sphere. Saturn's demanding and karmic influence on your destiny number ensures that themes of hard work, discipline, and the responsible use of power are central to your life journey. Your path is one of building, achieving, and leaving a lasting legacy.\n\nDN 8 is often associated with financial success and business acumen, but it also carries significant karmic weight. Saturn, the planet of karma, ensures that your rewards are directly proportional to your efforts and the integrity with which you operate. You cannot cut corners on the path of DN 8. The universe will hold you accountable, and shortcuts taken will inevitably lead to setbacks. However, when you operate with discipline, honesty, and sustained effort, the rewards can be extraordinary.\n\nYou are destined to develop executive capabilities and to demonstrate that you can handle significant responsibility. This may manifest through corporate leadership, entrepreneurship, financial management, or any other field where strategic thinking and the ability to manage resources and people are paramount. You have the potential to build something truly lasting, something that makes a difference not just in your own life but in the lives of many others.\n\nOne of the key challenges of DN 8 is maintaining balance between your material ambitions and your personal and spiritual life. Saturn's relentless drive for achievement can lead to workaholism and the neglect of relationships, health, and inner development. Learning to honor all dimensions of your life and to recognize that true success encompasses wellbeing, love, and wisdom, not just material achievement, will be one of the most transformative lessons of your journey.",

    9: "It is ruled by Mars.\n\nDestiny number 9 represents completion, universal compassion, and the fulfillment of your purpose through service to humanity. You are destined to be an inspiration to others, to champion important causes, and to leave the world a better place than you found it. Mars's passionate and courageous influence on your destiny number ensures that idealism, compassion, and a burning desire to make a difference are central themes throughout your life. You are meant to live for something larger than yourself.\n\nDN 9 is the number of the humanitarian, and you will find throughout your life that your most meaningful experiences and greatest fulfillments come through giving, serving, and contributing to the wellbeing of others. You have a broad and inclusive perspective that allows you to see beyond personal, cultural, or national boundaries, and you feel a genuine kinship with all of humanity. This expansive compassion is one of your most precious gifts and one of the cornerstones of your destiny.\n\nYour path is also one of completion and release. DN 9 carries within it the energy of all the numbers that precede it, and part of your destiny is to integrate the lessons of all those experiences and to release what no longer serves your highest growth. You may find that you go through several distinct phases or chapters in your life, each one requiring you to let go of what has been accomplished and to open yourself to a new cycle of experience and growth.\n\nOne of the key lessons of DN 9 is learning to channel your idealism and passion in practical directions. There can be a tendency to scatter your energy across too many causes or to burn yourself out in the service of others. Learning to focus your tremendous compassion and drive, to complete what you begin, and to honor your own needs as well as those of others will enable you to sustain your service and to realize the full power of your extraordinary destiny.",
}

LOVE_SEX_PDF_DATA = {
    1: "As a Destiny Number 1, you approach love and intimacy with the same boldness and directness that you bring to all aspects of life. You are passionate, determined, and fully invested when you choose to commit to a partner. You need a relationship where you can maintain your independence while also feeling deeply connected. A partner who admires your strength and supports your ambitions will bring out the very best in you.\n\nYou tend to take the lead in romantic relationships and prefer a partner who appreciates your initiatives. You are generous and warm with those you love, though you may sometimes prioritize your own desires and goals above your partner's needs. Learning to truly listen and respond to your partner's emotional world will deepen your connections significantly.\n\nIn the bedroom, your passion and confidence make you an attentive and energetic partner. You enjoy being in control and creating memorable experiences. The key to lasting fulfilment is learning to balance your natural dominance with a genuine openness to your partner's desires and needs.",

    2: "With Destiny Number 2, your love life is characterized by deep emotion, tenderness, and a profound desire for closeness and security. You are one of the most romantic and devoted partners in the numerology spectrum. You love deeply and give fully in relationships, creating an atmosphere of warmth, intimacy, and genuine emotional connection. For you, love is not just a feeling but a sacred bond.\n\nYou are highly attuned to your partner's moods and needs, often sensing what they feel before they express it. This sensitivity is your greatest romantic gift, but it can also make you vulnerable to hurt and disappointment. You may find yourself giving far more than you receive and need to ensure that your emotional needs are also being met in your relationships.\n\nIntimacy with a Destiny Number 2 individual is tender, sensual, and deeply meaningful. You prefer slow, romantic encounters filled with emotional presence over purely physical experiences. Touch, closeness, and genuine emotional connection are what fuel your deepest satisfaction in love.",

    3: "Destiny Number 3 brings a joyful, playful, and creatively expressive quality to your love life. You are charming, romantic, and naturally magnetic, drawing partners to you with your wit, warmth, and infectious enthusiasm. You approach relationships with an open heart and a spirit of adventure, always looking for ways to keep the spark alive and the connection vibrant. Love, for you, is one of life's greatest sources of joy and inspiration.\n\nYou are a natural flirt and enjoy the art of courtship and romance. You express your love through words, gestures, and creative acts, and you appreciate partners who can match your expressiveness and keep up with your lively spirit. Boredom is your greatest romantic adversary, and you need variety, humor, and genuine mental stimulation to keep you engaged and committed.\n\nIn intimate moments, you bring creativity, playfulness, and genuine warmth. You thrive when your partner appreciates your efforts at romance and reciprocates with their own expressions of affection. The key to lasting love for you is finding someone who can engage your mind as well as your heart.",

    4: "Navigating emotions, especially understanding your partner's passions, may pose challenges for you. Your approach to lovemaking is deliberate, preferring a slow and steady buildup of intensity.\n\nRelationships hold great significance for you, and your loyalty is unwavering. However, overthinking the task of making your partner happy can make lovemaking feel more like a duty than an expression of passion. To avoid stagnation, balance your intellectual approach with a willingness to explore new methods of arousal.\n\nIn your optimal state with a 4 Destiny Number, you embody solidity, loyalty, and accessibility. Tactile yet practical techniques characterize your approach in the bedroom, as you value a certain level of sexual engagement for balance.\n\nAs a no-nonsense lover, you excel in mastering techniques and may benefit from a partner with a more experimental spirit to introduce variety. Alternatively, you find fulfilment in a predictable yet satisfying sexual routine.\n\nObstacles may arise from an aversion to settling down, manifesting as bed-hopping and fear of emotional connection. To avoid a sexual rut, consider alternating between slow, gentle encounters and occasional wild experiences, or even trying outdoor lovemaking. For ladies, embracing the color green can amplify your sensual side.",

    5: "With Destiny Number 5, your approach to love and intimacy is characterized by a love of freedom, variety, and the thrill of discovery. You are adventurous and spontaneous in relationships, always seeking new ways to explore and deepen your connection with your partner. You resist routine and thrive when your relationship feels fresh, exciting, and full of possibility. You need a partner who can embrace your free spirit rather than trying to contain it.\n\nYou are naturally charming and attractive, and you typically have no shortage of romantic interest. Your challenge is finding a partner who can hold your attention for the long term. Once you do find someone who stimulates your mind and matches your zest for life, you are capable of deep and genuine commitment. The key is ensuring that the relationship continues to grow and evolve rather than stagnating.\n\nIn intimate moments, you bring energy, creativity, and a sense of fun. You enjoy variety and experimentation, and you are most fulfilled with a partner who is open-minded and adventurous. Keeping the physical and emotional dimensions of your relationship fresh and unpredictable is the secret to your long-term happiness in love.",

    6: "Destiny Number 6 makes you one of the most devoted, nurturing, and romantically generous partners in all of numerology. You love deeply and completely, investing your heart, time, and energy fully into the relationships that matter to you. Creating a loving, harmonious, and beautiful environment for your partner and family is one of your greatest sources of joy and fulfilment. Love, for you, is an act of service and a calling.\n\nYou are deeply sensual and appreciate the beauty and tenderness that intimacy can bring. You are attentive to your partner's needs and derive great pleasure from making them feel cherished and cared for. However, your deep desire to give and to please can sometimes tip into self-sacrifice, and it is important for you to also receive love and appreciation in return. A relationship where you feel truly valued will bring out your most radiant and generous self.\n\nIn intimate moments, you are warm, sensual, and deeply present. You prefer romantic and emotionally connected encounters over purely physical ones, and you thrive when love is expressed in all the small everyday gestures of care and devotion. Learning to openly express your own needs and desires as well as attending to your partner's is the key to your deepest fulfilment in love.",

    7: "You possess a dreamy and romantic nature, harboring a secret desire for a spiritual connection with your lover. Intellect holds great importance for you, emphasising the need to trust both your partner and yourself. Overanalyzing situations may cause you to miss out on profound connections, so it's essential to relax and let go occasionally. In your optimal state with a 7 Destiny Number, you embody mystery, analytical prowess, and deep thinking.",

    8: "With Destiny Number 8, your approach to love is shaped by the same qualities that define your professional life — intensity, loyalty, high standards, and a deep desire for genuine partnership. You take relationships seriously and are not interested in superficial connections. When you commit to someone, you do so with your full self and expect the same level of dedication and respect in return. A relationship, for you, is a partnership of equals built on mutual respect and shared goals.\n\nYou may not always be the most demonstrative or emotionally expressive partner, but your depth of feeling runs very deep. You show love through acts of provision, loyalty, and protection rather than through words or grand romantic gestures. Your partner will always know they can rely on you, and your steadfast commitment is one of your most profound gifts in a relationship.\n\nIn intimate moments, your intensity and passion are formidable. You bring the same focus and power to your love life as you do to your professional pursuits. The key for you is learning to be vulnerable and to allow your partner to see beyond your formidable exterior to the passionate, deeply feeling person within. Relationships that allow for both strength and vulnerability are the ones that will bring you the deepest satisfaction.",

    9: "Destiny Number 9 brings a passionate, idealistic, and deeply generous quality to your love life. You love with great intensity and give freely of yourself in relationships, often putting your partner's needs and happiness above your own. You have high ideals when it comes to love and are drawn to deep, meaningful connections that feel purposeful and transcendent. For you, a great love is one of the most precious experiences life can offer.\n\nYou are fiercely loyal once you have given your heart and can love with a depth that few can match. However, your tendency to idealize your partner may lead to disappointment when reality falls short of your romantic vision. Learning to love the real person in front of you, with all their human imperfections, is one of your most important lessons in love.\n\nIn intimate moments, you bring passion, generosity, and a desire for deep connection. You thrive when your relationship has both emotional depth and physical intensity, and you are most fulfilled when love is experienced as a profound meeting of souls. Taking time to communicate openly with your partner about your deepest needs and desires will help you build the truly extraordinary love that you deserve.",
}

LOVE_SEX_DATA = {
    1: "Passionate and dominant lover. Strong physical attraction. Independent in relationships - needs space. Can be self-centered. Best with partners who admire their strength.",
    2: "Romantic, tender, and deeply emotional. Craves intimacy and closeness. Highly sensitive to partner's needs. Can become too dependent. Needs reassurance.",
    3: "Playful, flirtatious, and creative in love. Needs mental stimulation and fun. Can be inconsistent in emotions. Keeps relationships lively with humor and spontaneity.",
    4: "Deliberate, slow and steady buildup of intensity. Loyalty is unwavering. Overthinking can make lovemaking feel like a duty. Balance intellectual approach with willingness to explore. Practical yet deeply committed.",
    5: "Adventurous and experimental lover. Needs variety and excitement. Can be commitment-phobic. Charming and irresistible. Best with open-minded partners.",
    6: "Deeply romantic, sensual, and devoted. Creates beautiful experiences for partner. Gives everything in love. Can be overly possessive. Needs to feel cherished and valued.",
    7: "Dreamy and romantic, harbors secret desire for spiritual connection. Intellect holds great importance. Trust is essential. Avoid overanalyzing or you miss profound connections. Mystery and deep thinking characterize your style.",
    8: "Intense and powerful lover. Views relationships as partnerships of equals. Can be controlling. Needs loyalty and respect. Deeply passionate beneath the serious exterior.",
    9: "Passionate, generous, and idealistic in love. Can fall hard and fast. Prone to putting partners on pedestals. Needs to avoid being too self-sacrificing. Deeply loyal once committed.",
}

CONNECTION_DATA = {
    1: "Step into your leadership role with confidence. Trust your instincts and pioneering ideas. Develop your independence and unique identity. Avoid imitating others - your originality is your greatest strength.",
    2: "Nurture your relationships with care and sensitivity. Develop your intuition and trust your inner voice. Practice diplomacy in all interactions. Your gift for harmony can create beautiful partnerships.",
    3: "Cultivate creativity through dancing, acting, poetry, or writing. Nurture self-confidence and embrace a more relaxed attitude. Draw inspiration from successful creative people around you.",
    4: "Enhance your reliability and punctuality by incorporating practical, organised, systematic approaches. Prioritise attention to details. Engage in outdoor and physical activities for self-discovery. Steer clear of procrastination.",
    5: "Embrace change and seek new experiences. Develop your communication skills and versatility. Travel, learn new skills, and stay curious. Your adaptability is your superpower.",
    6: "Focus on creating harmony in your home and relationships. Nurture your artistic side and beautify your environment. Practice unconditional love and service. Family bonds are your foundation.",
    7: "Deepen your spiritual practice and inner life. Spend time in solitude for reflection and study. Trust your powerful intuition. Explore metaphysical subjects and seek deeper meanings in life.",
    8: "Channel your ambition into structured, long-term goals. Develop financial intelligence and business acumen. Balance material pursuits with personal relationships. Your persistence will bring great rewards.",
    9: "Embrace your humanitarian impulses and serve a greater cause. Release what no longer serves you and make room for new experiences. Your compassion and wisdom inspire those around you.",
}

PERSONALITY_DATA = {
    1: "You project an image of confidence, authority and independence. People see you as a natural leader with a strong presence. Your pioneering spirit and bold approach to life make you stand out in any crowd.",
    2: "You project an image of gentleness, diplomacy and cooperation. People see you as a peacemaker and a good listener. Your warm, caring nature makes others feel comfortable and understood in your presence.",
    3: "Your energy radiates vitality and vibrancy. You possess a captivating and inspiring aura that uplifts those around you. Your charming nature and infectious personality make you a delight to be with. Your wit makes you the centre of attention.",
    4: "You project an image of reliability, stability and practicality. People see you as dependable and hardworking. Your methodical and organised approach to life gives others confidence that things will be done right.",
    5: "You possess a remarkable ability to stimulate and energize those around you. Social gatherings come alive in your presence as you infuse them with fresh and original ideas. Your conversations are characterized by a delightful blend of novelty, wit and charismatic charm.",
    6: "You project an image of warmth, nurturing and responsibility. People see you as caring, supportive and trustworthy. Your natural ability to create harmony and beauty makes you a beloved presence in any setting.",
    7: "You project an image of mystery, depth and intelligence. People are drawn to your quiet wisdom and introspective nature. Your analytical mind and spiritual depth give you an aura of profound understanding.",
    8: "You project an image of power, authority and success. People see you as ambitious, capable and in control. Your executive presence and business-like manner command respect and inspire confidence.",
    9: "You project an image of wisdom, compassion and universal love. People see you as inspiring, idealistic and deeply human. Your broad perspective and genuine concern for others makes you a natural humanitarian.",
}

SOUL_URGE_DATA = {
    1: "Deep desire to be independent and lead. Want to be first, original and self-sufficient. Crave recognition for unique accomplishments. Inner drive to stand on own two feet.",
    2: "Deep desire for love, harmony and connection. Want peace in all relationships. Crave partnership and belonging. Inner need to feel needed and appreciated.",
    3: "Deep desire to express yourself creatively. Want to entertain, inspire and uplift others. Crave social connection and joyful experiences. Inner need for appreciation of creative gifts.",
    4: "Want to be realistic, practical and intelligent. Want to create fixed assets and securities at earliest in life. Always want to remain organised. Want to be respected everywhere. Inner desire to serve others systematically.",
    5: "Deep desire for freedom and adventure. Want to experience everything life has to offer. Crave variety, travel and new experiences. Inner need to feel unrestricted and alive.",
    6: "Every penny is for family. Wants beautiful things in life. Wants to be cherished by family and close group of friends. Offers genuine help to others. Life sums up to Love, Friendship and Family.",
    7: "Deep desire for knowledge and spiritual truth. Want to understand the mysteries of life. Crave solitude and deep thinking. Inner need to find meaning beyond the material world.",
    8: "Deep desire for power, wealth and achievement. Want to build something lasting and significant. Crave recognition for accomplishments. Inner drive to succeed in material world.",
    9: "Deep desire to make the world a better place. Want to give freely and serve humanity. Crave universal love and acceptance. Inner need to live a life of meaning and purpose.",
}

FIRST_LETTER_DATA = {
    'A': "Natural leader with strong willpower. Independent, determined and ambitious. Highly creative with original ideas. Can be stubborn and self-centered at times. Strong drive to succeed on own terms.",
    'B': "Sensitive, cooperative and emotionally intuitive. Natural mediator with strong people skills. Deeply caring and devoted in relationships. Can be overly sensitive and indecisive.",
    'C': "Creative, expressive and optimistic. Wonderful communicator with a great sense of humor. Naturally social and uplifting to others. Can scatter energy and avoid difficult tasks.",
    'D': "Practical, disciplined and hardworking. Dependable and thorough in all endeavors. Strong builder with great organizational skills. Can be stubborn and resistant to change.",
    'E': "Versatile, freedom-loving and quick-minded. Excellent communicator and natural adventurer. Highly adaptable to new situations. Can be restless and inconsistent.",
    'F': "Responsible, caring and family-oriented. Natural nurturer with a strong sense of duty. Artistic and appreciates beauty. Can be self-sacrificing and worrisome.",
    'G': "Analytical, introspective and spiritually inclined. Deep thinker with strong intuition. Seeks perfection and truth. Can be secretive and overly critical.",
    'H': "Sociable, enjoyable to be around, and possessing notable intelligence. Highly prioritises freedom and independence. Remarkable sense of humour adds to their charm. Nurturing and empathetic towards others. Strong affinity for good music, food, drinks and art. Can become overly ambitious and selfish. Tires easily in physical activities.",
    'I': "Compassionate, artistic and highly sensitive. Deep humanitarian instincts. Strongly intuitive and emotionally aware. Can be moody and self-pitying.",
    'J': "Initiator with strong leadership qualities. Independent, determined and resourceful. Excellent at starting new projects. Can be impatient and domineering.",
    'K': "Highly cooperative with a charismatic personality. In touch with emotions and relies on intuition. Excels at entertaining others. Deep love for nurturing people and emotions. Ability to motivate and inspire. May encounter sudden events or losses. Fortunate financially with potential to become wealthy.",
    'L': "Analytical, detail-oriented and highly intelligent. Strong sense of justice and fairness. Excellent problem-solver. Can be overly critical and indecisive.",
    'M': "Hardworking, practical and deeply responsible. Strong maternal/paternal instincts. Highly reliable and dependable. Can be rigid and overly cautious.",
    'N': "Creative, intuitive and imaginative. Strong mental energy and quick thinking. Passionate and intense in pursuits. Can be nervous and unpredictable.",
    'O': "Responsible, compassionate and deeply committed. Strong sense of justice and fairness. Natural counselor and advisor. Can be self-righteous and overly cautious.",
    'P': "Intellectual, philosophical and spiritually aware. Seeks knowledge and deeper understanding. Strong powers of concentration. Can be secretive and isolated.",
    'Q': "Powerful, mysterious and highly intuitive. Strong leadership with unique perspectives. Excellent at reading situations. Can be suspicious and demanding.",
    'R': "Compassionate, humanitarian and deeply responsible. Strong work ethic and practical skills. Inspires others through example. Can be scattered and overly emotional.",
    'S': "Intense, emotional and highly magnetic. Natural initiator with strong willpower. Excellent at transformation and renewal. Can be secretive and obsessive.",
    'T': "Sensitive, intuitive and spiritually inclined. Natural healer and peacemaker. Strong sense of rhythm and creativity. Can be self-doubting and overly emotional.",
    'U': "Highly intuitive, humanitarian and universally minded. Strong spiritual awareness. Generous and compassionate. Can be impractical and escapist.",
    'V': "Practical, hardworking and highly capable. Excellent builder and organizer. Strong business instincts. Can be rigid and workaholic.",
    'W': "Versatile, communicative and highly social. Natural entertainer and storyteller. Quick-witted and adaptable. Can be scattered and superficial.",
    'X': "Intense, passionate and highly perceptive. Strong regenerative abilities. Excellent at research and investigation. Can be obsessive and secretive.",
    'Y': "Independent, spiritual and highly intuitive. Strong desire for freedom and truth-seeking. Natural philosopher. Can be indecisive and isolated.",
    'Z': "Optimistic, energetic and highly determined. Natural leader with infectious enthusiasm. Excellent at completing what others start. Can be impatient and domineering.",
}

SUCCESS_DATA = {
    1: {"qualities": "Leadership, originality and pioneering spirit define your success path. You have the drive to be first and blaze new trails. Your confidence and determination inspire others.", "challenges": "Avoid arrogance and learn to collaborate. Success grows when you empower others rather than dominating them."},
    2: {"qualities": "Diplomacy, cooperation and sensitivity are your keys to success. You excel in partnerships and create harmony wherever you go. Your intuition is a powerful guide.", "challenges": "Overcome indecisiveness and lack of confidence. Learn to stand firm in your own worth and value."},
    3: {"qualities": "Dynamic, creative and social. You convey the image of the joker, the entertainer and the mastermind of creativity. Your personality is characterised by humour, wit, intelligence and sociability. Inherently joyful, you spread happiness to those around you.", "challenges": "Fear of criticism or emotional baggage may suppress your dreams. The strong desire for social acceptance can lead you to compromise your remarkable creative abilities."},
    4: {"qualities": "Discipline, organization and practicality define your success. You build lasting foundations and see projects through to completion. Your reliability makes you invaluable.", "challenges": "Avoid rigidity and learn to adapt. Balance hard work with rest and relationships."},
    5: {"qualities": "Versatility, freedom and communication are your strengths. You adapt quickly and excel in dynamic environments. Your ability to connect with diverse people opens many doors.", "challenges": "Develop consistency and follow-through. Scattered energy and restlessness can undermine your many talents."},
    6: {"qualities": "Responsibility, nurturing and harmony define your success. You excel at creating beautiful, functional environments and caring for others. Your artistic sensibility and warm heart draw people to you.", "challenges": "Avoid martyrdom and learn healthy boundaries. Your tendency to sacrifice yourself for others can lead to resentment."},
    7: {"qualities": "Wisdom, analysis and spiritual insight are your success keys. You excel at research, investigation and finding hidden truths. Your depth of understanding gives you unique perspectives.", "challenges": "Avoid isolation and over-analysis. Share your insights with the world rather than keeping them to yourself."},
    8: {"qualities": "Ambition, authority and material mastery define your success. You excel at business, leadership and building financial security. Your executive abilities and determination create lasting achievements.", "challenges": "Avoid workaholism and ruthlessness. True success includes fulfilling personal relationships and good health."},
    9: {"qualities": "Compassion, wisdom and universal understanding are your greatest gifts. You inspire others through your idealism and generous spirit. Your broad perspective sees the big picture.", "challenges": "Avoid martyrdom and impracticality. Learn to complete projects and follow through on commitments."},
}

MATURITY_DATA = {
    1: "In your later years, you will increasingly value independence and self-reliance. A desire to lead and make your unique mark on the world will grow stronger. You may start new ventures or pursue long-held dreams with renewed determination.",
    2: "In your later years, relationships and emotional fulfillment will take center stage. You will seek deeper connections and meaningful partnerships. Your wisdom in diplomacy and understanding human nature will make you a valued counselor.",
    3: "In your later years, creative self-expression will become increasingly important. You will seek to express your authentic self through art, writing or communication. Your natural optimism and joy will radiate more strongly.",
    4: "As you enter later life, you will notice a shift towards practicality, organisation and concern for material achievements. You will turn ideas into practical realities. A deep desire for material success and respect persists. Legacy-building and strengthening family bonds become priorities. Avoid becoming rigid or overly work-focused.",
    5: "In your later years, freedom and adventure will remain important. You will seek new experiences and resist being tied down. Your adaptability will serve you well through life changes. Travel and learning keep your spirit young.",
    6: "In your later years, love, family and community will be your greatest sources of fulfillment. You will take on a nurturing, wise elder role. Creating beauty and harmony in your environment becomes deeply satisfying.",
    7: "As you mature, this number carries a philosophical and inherently wise energy. You will gradually let go of mundane aspects and expand mental horizons. Reading, contemplation and searching for Truths becomes central. Drawn to metaphysical subjects. Intuition sharpens. Need for privacy grows. Avoid excessive solitude.",
    8: "In your later years, the desire for achievement and material security intensifies. You will be drawn to positions of power and influence. Financial planning and building lasting legacy become central concerns. Balance ambition with wisdom.",
    9: "In your later years, humanitarian impulses and spiritual wisdom will come to full expression. You will be drawn to service, teaching and sharing your life wisdom. Letting go of the personal in favor of the universal brings deep peace.",
}

PERSONAL_YEAR_DATA = {
    1: {
        "title": "Year of New Beginnings, Fresh Starts and Independence",
        "positive": "New opportunities open up. Increased energy and motivation. Excellent for starting new projects, businesses or relationships. Seeds planted now will flourish.",
        "negative": "May feel restless and impatient. Risk of acting impulsively. Old structures may fall away causing temporary discomfort.",
        "luck": {"M1": 90, "M2": 70, "M3": 80, "M4": 60, "M5": 75, "M6": 65, "M7": 55, "M8": 70, "M9": 85},
    },
    2: {
        "title": "Year of Cooperation, Relationships and Patience",
        "positive": "Relationships deepen and flourish. Good year for partnerships and collaborations. Intuition is heightened. Emotional healing occurs.",
        "negative": "May feel overly sensitive or indecisive. Progress seems slow. Avoid confrontations and hasty decisions.",
        "luck": {"M1": 65, "M2": 90, "M3": 70, "M4": 75, "M5": 60, "M6": 85, "M7": 80, "M8": 55, "M9": 70},
    },
    3: {
        "title": "Year of Creativity, Expression and Social Expansion",
        "positive": "Creative energy is high. Social life flourishes. Excellent for artistic projects, communication and networking. Joy and optimism abound.",
        "negative": "Risk of scattering energy. May be superficial or avoid serious responsibilities. Watch spending.",
        "luck": {"M1": 80, "M2": 70, "M3": 90, "M4": 65, "M5": 75, "M6": 70, "M7": 60, "M8": 55, "M9": 85},
    },
    4: {
        "title": "Year of Stability, Security and Hard Work",
        "positive": "Will keep you in illusion for first 2 months then develop practicality. You become very practical. A sense of security will develop. Time to set a routine and build a system. Be aware and take care of your health.",
        "negative": "Low energy levels. Will feel pressurised. Days will go rigid and slow. You will be frustrated. Must do hard work to earn - cannot rely on luck.",
        "luck": {"M1": 100, "M2": 75, "M3": 70, "M4": 85, "M5": 60, "M6": 80, "M7": 65, "M8": 90, "M9": 55},
    },
    5: {
        "title": "Year of Change, Freedom and Adventure",
        "positive": "Exciting changes and new opportunities. Travel and new experiences. Increased freedom and flexibility. Dynamic energy brings breakthroughs.",
        "negative": "Instability and unpredictability. Difficulty maintaining routines. Risk of making hasty decisions. Scattered focus.",
        "luck": {"M1": 70, "M2": 60, "M3": 75, "M4": 65, "M5": 90, "M6": 55, "M7": 80, "M8": 70, "M9": 85},
    },
    6: {
        "title": "Year of Love, Family and Responsibility",
        "positive": "Family relationships strengthen. Home improvements and beautification. Opportunities for healing relationships. Creative and artistic endeavors flourish.",
        "negative": "Increased responsibilities and obligations. May feel burdened by demands of others. Avoid meddling in others affairs.",
        "luck": {"M1": 65, "M2": 85, "M3": 70, "M4": 75, "M5": 55, "M6": 90, "M7": 60, "M8": 70, "M9": 80},
    },
    7: {
        "title": "Year of Reflection, Spirituality and Inner Growth",
        "positive": "Deep spiritual insights and personal growth. Excellent for study, research and self-discovery. Intuition is very strong. Inner wisdom develops.",
        "negative": "May feel isolated or withdrawn. Material progress is slow. Avoid major financial decisions. Not a year for aggressive action.",
        "luck": {"M1": 55, "M2": 80, "M3": 65, "M4": 70, "M5": 75, "M6": 60, "M7": 90, "M8": 65, "M9": 85},
    },
    8: {
        "title": "Year of Power, Achievement and Financial Growth",
        "positive": "Career advancement and financial opportunities. Increased authority and recognition. Excellent for business expansion and investments. Hard work brings substantial rewards.",
        "negative": "Risk of overwork and burnout. Power struggles may arise. Avoid cutting corners or unethical shortcuts. Balance ambition with health.",
        "luck": {"M1": 75, "M2": 60, "M3": 65, "M4": 85, "M5": 70, "M6": 75, "M7": 55, "M8": 90, "M9": 70},
    },
    9: {
        "title": "Year of Completion, Release and Transformation",
        "positive": "Completion of long cycles. Letting go brings liberation. Humanitarian work is rewarding. Wisdom and compassion grow. Preparation for new cycle ahead.",
        "negative": "Endings can be painful. Must release what no longer serves. Avoid starting major new projects - this is a time of completion. Emotional intensity.",
        "luck": {"M1": 85, "M2": 70, "M3": 80, "M4": 60, "M5": 75, "M6": 70, "M7": 80, "M8": 65, "M9": 90},
    },
}

LOSHU_INTERPRETATIONS = {
    1: {1: "Self-confident, expressive and vocal. Good communication skills. Natural ability to connect with others.", 2: "Strong communicator but may sometimes overexplain. Good at influencing others through words.", 3: "Difficulty vocalizing thoughts despite strong opinions. May attract conflicts through speech. Tendency to overexplain. Hard to say no. Can become dependent on others."},
    2: {1: "Balanced intuition and emotional sensitivity. Good family values and relationships.", 2: "Very family-oriented - family is everything. Highly intuitive with almost always correct instincts. Sensitive and emotionally driven.", 3: "Extremely sensitive and emotional. May be overly dependent on family. Strong psychic abilities but can be overwhelmed by emotions."},
    3: {1: "Sharp-minded, creative and knowledgeable. Exemplary imagination. Learns fast and plans efficiently. May experience delay in success but gets there eventually. Both business and job suit equally.", 2: "Highly creative with strong intellectual capabilities. Excellent planner and executor of ideas.", 3: "Exceptional creativity and intelligence. Natural teacher and knowledge-sharer. May become impatient with slower minds."},
    4: {1: "Practical and hardworking. Excellent hand-related skills like cooking, sewing, coding, playing instruments. Gets unique revolutionary ideas. Proficient in debates. Law is suitable career. Believes in multiple income sources. Dislikes grey areas.", 2: "Very practical and disciplined. Strong financial instincts and investment mindset.", 3: "Extremely hardworking but may become rigid. Exceptional practical skills. Must balance work with rest."},
    5: {1: "Balanced personality. Good connector between different areas of life. Practical and adaptable.", 2: "Strong mediating abilities. Excellent at balancing opposing forces. Natural diplomat.", 3: "Extremely versatile but may lack direction. Exceptional communication skills. Needs to focus energy productively."},
    6: {1: "Artistic sensibilities and appreciation for beauty. Caring and family-oriented. Good financial instincts.", 2: "Strong creative abilities and aesthetic sense. Very nurturing and family-devoted.", 3: "Exceptional artistic talent. Extremely family-focused. May neglect own needs for others. Strong healing abilities."},
    7: {1: "Blessed with intuitive powers that guide down right path. Family and children supportive. Respects all relationships. Always learns from mistakes. Dissatisfaction and heartbreaks likely in one area. Spirituality will knock early.", 2: "Very spiritually inclined. Strong intuition and healing abilities. Deep bond with family.", 3: "Exceptional spiritual gifts. May feel caught between material and spiritual worlds. Powerful healer and mystic."},
    8: {1: "Good financial awareness and practical wisdom. Learns valuable life lessons through hardships.", 2: "Strong financial acumen and business sense. Excellent at managing resources.", 3: "Exceptional material success potential. Very disciplined and ambitious. May become overly focused on material gain."},
    9: {1: "Highly ambitious from early age with immense willpower. Kind and helps others selflessly. Prefers giving orders over taking them. Forgives but never forgets insults. Promised high energy for any task.", 2: "Very humanitarian and generous. Strong leadership qualities. High energy and ambition.", 3: "Enjoys being appreciated. Straightforward and very generous with humanitarian intentions. May overlook opinions of others. Needs to channel energy surges through physical activities."},
}

MISSING_NUMBER_DATA = {
    1: {"impact": "No ego, low self-confidence, introverted, problems expressing experiences, face career problems.", "remedy_day": "Sunday", "remedy": "Donate Jaggery. Wear: Bloodstone + Tiger Eye bracelet. Chant: Om Shreem Suryay Namh. Yantra: Surya Yantra. Rudraksh: 1 Mukhi & 12 Mukhi."},
    2: {"impact": "Problems in love relations, lack of stability and patience, live in imaginations, lack of intuition and self-confidence.", "remedy_day": "Monday", "remedy": "Donate white things. Wear: Mother of Pearl + Howlite bracelet. Chant: Om shram shreem shraum sah chandramasaye namah. Yantra: Chandra Yantra. Rudraksh: 2 Mukhi."},
    3: {"impact": "Less grace of Guru and lord, problems in promotion and growth, lack of creative thinking, low self-confidence, easily distracted.", "remedy_day": "Thursday", "remedy": "Donate Yellow things. Wear: Natural Turquoise + Natural Amazonite bracelet. Chant: Om Gram greem groum sah gurave naman. Yantra: Guru Yantra. Rudraksh: 5 Mukhi."},
    4: {"impact": "Lack of financial stability and growth, lack of intuition power, struggle to achieve success, becomes directionless, weak thought power.", "remedy_day": "Saturday", "remedy": "Donate Black things and alcohol (to reduce its effect). Wear: Black Agate + 7 chakra bracelet. Chant: Om bhram bhreem bhroum sah rahave namah. Yantra: Rahu Yantra. Rudraksh: 5 Mukhi."},
    5: {"impact": "Lack of stability and self-confidence, health problems related to stomach and back pain, trouble starting work, loss in business, problem making own house.", "remedy_day": "Wednesday", "remedy": "Donate Green things, Ghee, study material, teach free of cost. Wear: Green Zade + Green Aventurian bracelet. Chant: Om bram breem broum sah budhaya Namah. Yantra: Buddh Yantra. Rudraksh: 10 Mukhi."},
    6: {"impact": "Lack of money and luxury life, struggle to achieve success, shortage of good friends, family support not available at right time, problems in love relations due to introverted nature.", "remedy_day": "Friday", "remedy": "Donate perfumes, cashew and cosmetics. Wear: Rose Quartz + Dragon Vein bracelet. Chant: Om dram dreem droum sah shukraya namah. Yantra: Shukra Yantra. Rudraksh: 9 Mukhi."},
    7: {"impact": "Hindrance in work and studies, no family support, no success despite effort, struggle more than success, mental disturbance.", "remedy_day": "Wednesday", "remedy": "Donate Black Clothes and Blanket. Wear: Cat's Eye + Azurite bracelet. Chant: Om shram shreem shroum sah ketave namah (7000 times in 25 days). Yantra: Ketu Yantra. Rudraksh: 9 Mukhi."},
    8: {"impact": "Difficulty making financial decisions, no perfection in work, lack of motivation and stability, life has lots of ups and downs, poor health and wealth.", "remedy_day": "Saturday", "remedy": "Donate Chayadan and Mustard Oil. Wear: Amethyst + Black Agate bracelet. Chant: Om Pram Preem Prom sah shanayshcharaya namah. Yantra: Shani Yantra. Rudraksh: 7 Mukhi."},
    9: {"impact": "Lack of energy and drive, difficulty completing tasks, emotional volatility, challenges in humanitarian pursuits, disconnected from higher purpose.", "remedy_day": "Tuesday", "remedy": "Donate Red things and food to the poor. Wear: Red Coral + Carnelian bracelet. Chant: Om kram kreem kroum sah bhaumaya namah. Yantra: Mangal Yantra. Rudraksh: 3 Mukhi."},
}

CAREER_DATA = {
    (1,1): {"general": "Double Sun energy — extraordinary leadership and individuality. Natural pioneers with magnetic personalities.", "fields": "Entrepreneurship, Politics, Executive Management, Brand Building, Innovation", "strengths": "bold decision-making, original thinking, inspirational leadership", "challenges": "sharing credit, avoiding stubbornness"},
    (1,2): {"general": "Mulank 1 leaders with Bhagyank 2 cooperation. Balance between independence and teamwork.", "fields": "Diplomacy, HR Management, Counseling, Public Relations, Team Leadership", "strengths": "leading with empathy, building team harmony, diplomatic authority", "challenges": "overcoming indecisiveness, balancing independence with collaboration"},
    (1,3): {"general": "Mulank 1 pioneer with Bhagyank 3 creativity. Dynamic communicators and creative leaders.", "fields": "Media, Entertainment, Marketing, Creative Direction, Motivational Speaking", "strengths": "creative leadership, charismatic communication, innovative thinking", "challenges": "maintaining focus, avoiding scattered energy"},
    (1,4): {"general": "Mulank 1 individuals are natural leaders and innovators. Bhagyank 4 brings stability, discipline and practical approach.", "fields": "Business Management, Financial Planning, Project Management, Administration, Real Estate", "strengths": "leadership skills, practical approach, strong discipline", "challenges": "flexibility in changing environments, learning to delegate"},
    (1,5): {"general": "Mulank 1 leadership with Bhagyank 5 freedom and adaptability. Dynamic, versatile go-getters.", "fields": "Sales, Digital Marketing, Travel Industry, Media, Entrepreneurship", "strengths": "pioneering new ventures, adaptable leadership, excellent communication", "challenges": "consistency, avoiding impulsive decisions"},
    (1,6): {"general": "Mulank 1 independence with Bhagyank 6 nurturing. Leaders who build communities and care for others.", "fields": "Healthcare Administration, Education Leadership, Social Enterprise, Luxury Brands, Interior Design", "strengths": "empathetic leadership, community building, aesthetic vision", "challenges": "setting boundaries, avoiding martyrdom"},
    (1,7): {"general": "Mulank 1 pioneer with Bhagyank 7 wisdom. Leaders with deep analytical and spiritual insight.", "fields": "Research, Philosophy, Technology, Spiritual Leadership, Academia", "strengths": "original research, visionary thinking, deep analysis", "challenges": "sharing findings openly, practical implementation"},
    (1,8): {"general": "Mulank 1 ambition with Bhagyank 8 material mastery. Born for power and business success.", "fields": "Business Leadership, Finance, Real Estate, Investment, Corporate Law", "strengths": "executive power, financial acumen, determined achievement", "challenges": "work-life balance, avoiding ruthlessness"},
    (1,9): {"general": "Mulank 1 leadership with Bhagyank 9 humanitarian service. Leaders who change the world.", "fields": "NGO Leadership, Politics, Humanitarian Work, Social Reform, Philanthropy", "strengths": "inspiring leadership, compassionate vision, global perspective", "challenges": "practicality, follow-through on commitments"},
    (2,1): {"general": "Mulank 2 sensitivity with Bhagyank 1 leadership. Diplomatic leaders with strong emotional intelligence.", "fields": "Counseling, Human Resources, Diplomatic Service, Psychology, Mediation", "strengths": "emotional intelligence, diplomatic leadership, strong intuition", "challenges": "assertiveness, overcoming indecisiveness"},
    (2,2): {"general": "Double Moon energy — deeply intuitive, empathetic and relationship-focused.", "fields": "Counseling, Nursing, Social Work, Teaching, Creative Arts", "strengths": "deep empathy, intuition, harmony-building, emotional support", "challenges": "setting boundaries, developing self-confidence"},
    (2,3): {"general": "Mulank 2 expression with Bhagyank 3 creativity. Harmonious creative collaborators.", "fields": "Art, Music, Writing, Event Planning, Community Development", "strengths": "creative collaboration, emotional expression, social harmony", "challenges": "self-promotion, consistency in creative output"},
    (2,4): {"general": "Mulank 2 sensitivity with Bhagyank 4 practicality. Emotionally intelligent builders.", "fields": "Accounting, Administrative Management, Social Planning, Education, Project Coordination", "strengths": "careful planning, emotional sensitivity, reliable execution", "challenges": "speaking up, developing assertiveness"},
    (2,5): {"general": "Mulank 2 diplomacy with Bhagyank 5 versatility. Adaptable communicators.", "fields": "Public Relations, Tourism, Language Services, Writing, Customer Relations", "strengths": "communication, adaptability, emotional intelligence", "challenges": "commitment, avoiding over-sensitivity"},
    (2,6): {"general": "Mulank 2 nurturing with Bhagyank 6 responsibility. Natural caregivers and community builders.", "fields": "Healthcare, Education, Social Work, Family Counseling, Non-profit", "strengths": "deep empathy, family-centered service, nurturing leadership", "challenges": "self-care, setting healthy boundaries"},
    (2,7): {"general": "Mulank 2 intuition with Bhagyank 7 wisdom. Deeply spiritual and psychic individuals.", "fields": "Psychology, Healing Arts, Research, Spiritual Counseling, Philosophy", "strengths": "psychic intuition, deep analysis, spiritual guidance", "challenges": "practical application, avoiding isolation"},
    (2,8): {"general": "Mulank 2 sensitivity with Bhagyank 8 ambition. Emotionally intelligent business minds.", "fields": "Financial Counseling, HR Leadership, Wellness Business, Real Estate, Luxury Services", "strengths": "emotional intelligence in business, relationship-based success, intuitive financial sense", "challenges": "decisiveness, asserting authority"},
    (2,9): {"general": "Mulank 2 harmony with Bhagyank 9 service. Compassionate helpers dedicated to humanity.", "fields": "Social Work, Healing Arts, Non-profit Management, Teaching, International Aid", "strengths": "deep compassion, collaborative service, emotional healing", "challenges": "practical boundaries, avoiding martyrdom"},
    (3,1): {"general": "Mulank 3 creativity with Bhagyank 1 leadership. Charismatic creative leaders.", "fields": "Entertainment, Media, Marketing, Brand Strategy, Public Speaking", "strengths": "creative leadership, charisma, original communication", "challenges": "follow-through, maintaining discipline"},
    (3,2): {"general": "Mulank 3 expression with Bhagyank 2 cooperation. Creative collaborators with strong social skills.", "fields": "Art Therapy, Creative Collaboration, Community Arts, Writing, Performance", "strengths": "expressive creativity, team harmony, social charm", "challenges": "self-confidence, avoiding over-dependence on approval"},
    (3,3): {"general": "Double Jupiter energy — extraordinarily gifted communicators and creative thinkers.", "fields": "Writing, Performing Arts, Comedy, Broadcasting, Education", "strengths": "exceptional communication, infectious enthusiasm, creative brilliance", "challenges": "focus, avoiding superficiality"},
    (3,4): {"general": "Mulank 3 creativity with Bhagyank 4 practicality. Creative individuals who build lasting work.", "fields": "Architecture, Design, Publishing, Content Strategy, Educational Materials", "strengths": "creative discipline, structured expression, reliable creativity", "challenges": "avoiding rigid thinking, balancing freedom and structure"},
    (3,5): {"general": "Mulank 3 expression with Bhagyank 5 freedom. Dynamic communicators who love variety.", "fields": "Journalism, Travel Writing, Digital Content, Marketing, Advertising", "strengths": "versatile communication, adaptable creativity, engaging storytelling", "challenges": "consistency, depth over breadth"},
    (3,6): {"general": "Mulank 3 creativity with Bhagyank 6 love and beauty. Artistic creators who bring beauty to life.", "fields": "Interior Design, Fashion, Music, Art, Lifestyle Blogging", "strengths": "aesthetic creativity, warm expression, beauty-centered work", "challenges": "business acumen, valuing own work"},
    (3,7): {"general": "Mulank 3 individuals are creative, expressive and communicative. Bhagyank 7 brings intuition, spirituality and analytical depth.", "fields": "Content Creation for Spirituality, Holistic Healing Practitioner, Spiritual Counselling, Creative Writing/Authorship, Media Production", "strengths": "creative spirituality, intuitive problem solving, effective communication", "challenges": "balancing practicality and idealism, managing emotional depth"},
    (3,8): {"general": "Mulank 3 creativity with Bhagyank 8 ambition. Creative entrepreneurs with business acumen.", "fields": "Entertainment Business, Publishing, Creative Agency, Brand Management, Media Production", "strengths": "creative business sense, charismatic authority, expressive leadership", "challenges": "work-life balance, avoiding overcommitment"},
    (3,9): {"general": "Mulank 3 expression with Bhagyank 9 service. Creative humanitarians who inspire through art.", "fields": "Humanitarian Arts, Activism, Social Media, Teaching, Cultural Programs", "strengths": "inspiring communication, creative compassion, artistic service", "challenges": "practical follow-through, financial management"},
    (4,1): {"general": "Mulank 4 discipline with Bhagyank 1 independence. Practical pioneers who build lasting innovations.", "fields": "Engineering, Technology, Architecture, Business Founding, Project Management", "strengths": "disciplined innovation, practical leadership, structured building", "challenges": "flexibility, embracing new approaches"},
    (4,2): {"general": "Mulank 4 practicality with Bhagyank 2 harmony. Reliable team players who build stable structures.", "fields": "Accounting, Administrative Management, Social Planning, Education, Healthcare Administration", "strengths": "organized reliability, team support, careful planning", "challenges": "assertiveness, adaptability"},
    (4,3): {"general": "Mulank 4 stability with Bhagyank 3 creativity. Systematic creative workers.", "fields": "Graphic Design, Technical Writing, Educational Content, Music Production, Architecture", "strengths": "structured creativity, reliable execution, planned innovation", "challenges": "spontaneity, avoiding over-analysis"},
    (4,4): {"general": "Double Rahu energy — unconventional, practical and intensely hardworking.", "fields": "Technology, Engineering, Finance, Research, Real Estate", "strengths": "exceptional discipline, innovative thinking, strong work ethic", "challenges": "rigidity, avoiding workaholism"},
    (4,5): {"general": "Mulank 4 structure with Bhagyank 5 freedom. Practical adventurers who bring order to change.", "fields": "Travel Industry, Technology, Sales, Project Management, Consulting", "strengths": "organized adaptability, practical communication, structured flexibility", "challenges": "embracing uncertainty, avoiding rigidity"},
    (4,6): {"general": "Mulank 4 discipline with Bhagyank 6 nurturing. Practical caregivers and reliable community builders.", "fields": "Healthcare Administration, Education, Social Services, Family Business, Real Estate", "strengths": "reliable care, practical nurturing, organized service", "challenges": "emotional openness, work-life balance"},
    (4,7): {"general": "Mulank 4 practicality with Bhagyank 7 wisdom. Deep thinkers who build knowledge systems.", "fields": "Research, Academia, Technology, Philosophy, Data Analysis", "strengths": "analytical depth, structured research, practical wisdom", "challenges": "social connection, sharing findings"},
    (4,8): {"general": "Mulank 4 discipline with Bhagyank 8 ambition. Powerhouses of business success.", "fields": "Finance, Real Estate, Business Management, Investment, Corporate Strategy", "strengths": "exceptional financial discipline, strategic planning, powerful execution", "challenges": "flexibility, work-life balance"},
    (4,9): {"general": "Mulank 4 practicality with Bhagyank 9 service. Systematic humanitarians who build lasting change.", "fields": "Non-profit Management, Social Entrepreneurship, Development Work, Education, Healthcare", "strengths": "organized service, practical compassion, systematic change-making", "challenges": "emotional flexibility, avoiding rigidity in service"},
    (5,1): {"general": "Mulank 5 freedom with Bhagyank 1 leadership. Dynamic, adventurous pioneers.", "fields": "Entrepreneurship, Media, Travel, Sales, Technology", "strengths": "bold adaptability, pioneering communication, adventurous leadership", "challenges": "consistency, long-term commitment"},
    (5,2): {"general": "Mulank 5 versatility with Bhagyank 2 cooperation. Flexible, socially-skilled communicators.", "fields": "Public Relations, Customer Success, Tourism, Language, Mediation", "strengths": "adaptable diplomacy, excellent communication, social intelligence", "challenges": "stability, avoiding over-sensitivity"},
    (5,3): {"general": "Mulank 5 freedom with Bhagyank 3 creativity. Extraordinarily communicative and expressive.", "fields": "Journalism, Content Creation, Broadcasting, Advertising, Stand-up Comedy", "strengths": "versatile creativity, engaging communication, social charisma", "challenges": "depth, following through on projects"},
    (5,4): {"general": "Mulank 5 adaptability with Bhagyank 4 stability. Organized adventurers who bring structure to change.", "fields": "Technology, Consulting, Project Management, Training, Sales Management", "strengths": "structured adaptability, practical communication, organized freedom", "challenges": "patience with slow processes, maintaining routines"},
    (5,5): {"general": "Double Mercury energy — extraordinarily versatile, communicative and freedom-loving.", "fields": "Media, Travel, Sales, Marketing, Entrepreneurship", "strengths": "exceptional adaptability, brilliant communication, adventurous spirit", "challenges": "commitment, avoiding restlessness"},
    (5,6): {"general": "Mulank 5 freedom with Bhagyank 6 responsibility. Adventurous nurturers who serve with variety.", "fields": "Travel Therapy, Health Coaching, Family Services, Education, Lifestyle Brand", "strengths": "warm adaptability, caring communication, service with creativity", "challenges": "stability, avoiding over-commitment"},
    (5,7): {"general": "Mulank 5 versatility with Bhagyank 7 wisdom. Freedom-seeking wisdom seekers.", "fields": "Philosophy, Research, Spiritual Travel, Writing, Teaching", "strengths": "versatile wisdom, intuitive communication, spiritual exploration", "challenges": "practical grounding, consistency"},
    (5,8): {"general": "Mulank 5 freedom with Bhagyank 8 ambition. Dynamic business builders who thrive on change.", "fields": "Sales Leadership, Business Development, Entrepreneurship, Finance, Media", "strengths": "dynamic business acumen, adaptable authority, excellent networking", "challenges": "discipline, avoiding scattered energy"},
    (5,9): {"general": "Mulank 5 freedom with Bhagyank 9 service. Adventurous humanitarians who serve diverse communities.", "fields": "International Aid, Social Media Activism, Travel Journalism, Community Outreach, Education", "strengths": "versatile compassion, cross-cultural communication, dynamic service", "challenges": "commitment, focusing humanitarian energy"},
    (6,1): {"general": "Mulank 6 nurturing with Bhagyank 1 leadership. Compassionate leaders who build communities.", "fields": "Healthcare Leadership, Education Administration, Social Enterprise, Luxury Hospitality, Interior Design", "strengths": "empathetic leadership, aesthetic vision, community building", "challenges": "assertiveness, avoiding over-responsibility"},
    (6,2): {"general": "Mulank 6 care with Bhagyank 2 harmony. Ultimate nurturers and peacemakers.", "fields": "Social Work, Counseling, Teaching, Healthcare, Family Services", "strengths": "deep nurturing, exceptional empathy, harmony creation", "challenges": "self-care, boundaries"},
    (6,3): {"general": "Mulank 6 beauty with Bhagyank 3 creativity. Artistic nurturers who create beautiful expressions.", "fields": "Fine Arts, Music, Interior Design, Fashion, Culinary Arts", "strengths": "artistic nurturing, aesthetic creativity, warm expression", "challenges": "business skills, self-promotion"},
    (6,4): {"general": "Mulank 6 responsibility with Bhagyank 4 discipline. Reliable builders of beautiful, stable homes.", "fields": "Real Estate, Architecture, Family Business, Education, Healthcare Administration", "strengths": "responsible building, practical beauty, reliable nurturing", "challenges": "emotional flexibility, avoiding perfectionism"},
    (6,5): {"general": "Mulank 6 nurturing with Bhagyank 5 adventure. Caring free spirits who serve with variety.", "fields": "Travel Therapy, Health Coaching, Creative Teaching, Lifestyle Brand, International Aid", "strengths": "adaptable nurturing, creative service, warm communication", "challenges": "stability, avoiding over-commitment"},
    (6,6): {"general": "Double Venus energy — extraordinary beauty, love, and nurturing capacity.", "fields": "Healthcare, Fine Arts, Interior Design, Education, Social Services", "strengths": "exceptional empathy, artistic mastery, devoted service", "challenges": "martyrdom, setting boundaries"},
    (6,7): {"general": "Mulank 6 love with Bhagyank 7 wisdom. Spiritually-gifted healers and advisors.", "fields": "Healing Arts, Spiritual Counseling, Psychology, Philosophy, Sacred Music", "strengths": "spiritual wisdom, healing love, deep intuition", "challenges": "practical business, avoiding isolation"},
    (6,8): {"general": "Mulank 6 responsibility with Bhagyank 8 ambition. Nurturing business leaders.", "fields": "Healthcare Business, Luxury Brand Management, Education Leadership, Social Enterprise, Real Estate", "strengths": "responsible ambition, aesthetic authority, nurturing leadership", "challenges": "work-life balance, avoiding over-control"},
    (6,9): {"general": "Mulank 6 care with Bhagyank 9 service. Ultimate humanitarian caregivers.", "fields": "International Aid, Social Work, Healing Centers, Environmental Activism, Teaching", "strengths": "universal compassion, dedicated service, healing wisdom", "challenges": "personal boundaries, practical sustainability"},
    (7,1): {"general": "Mulank 7 wisdom with Bhagyank 1 leadership. Visionary leaders with deep analytical insight.", "fields": "Research Leadership, Technology, Philosophy, Academic Leadership, Spiritual Direction", "strengths": "visionary analysis, pioneering research, deep leadership", "challenges": "sharing insights, social engagement"},
    (7,2): {"general": "Mulank 7 depth with Bhagyank 2 cooperation. Intuitive collaborators with spiritual gifts.", "fields": "Psychology, Spiritual Counseling, Research Partnerships, Healing Arts, Mediation", "strengths": "psychic intuition, collaborative wisdom, healing presence", "challenges": "assertiveness, practical grounding"},
    (7,3): {"general": "Mulank 7 analysis with Bhagyank 3 creativity. Intellectually creative and deeply expressive.", "fields": "Scientific Writing, Spiritual Arts, Philosophy, Research Communication, Metaphysical Teaching", "strengths": "analytical creativity, deep communication, spiritual expression", "challenges": "practical execution, social engagement"},
    (7,4): {"general": "Mulank 7 wisdom with Bhagyank 4 discipline. Systematic researchers and knowledge builders.", "fields": "Science, Research, Data Analysis, Engineering, Philosophy", "strengths": "analytical precision, systematic research, practical wisdom", "challenges": "social connection, emotional expression"},
    (7,5): {"general": "Mulank 7 depth with Bhagyank 5 freedom. Wisdom-seeking adventurers and free thinkers.", "fields": "Spiritual Travel, Research Journalism, Philosophy, Academic Exploration, Writing", "strengths": "versatile wisdom, intuitive communication, analytical exploration", "challenges": "practical grounding, commitment"},
    (7,6): {"general": "Mulank 7 wisdom with Bhagyank 6 love. Spiritual healers and wise caregivers.", "fields": "Healing Arts, Spiritual Psychology, Sacred Music, Philosophy, Family Therapy", "strengths": "wise compassion, spiritual healing, intuitive care", "challenges": "practical application, social boundaries"},
    (7,7): {"general": "Double Ketu energy — extraordinarily spiritual, analytical and mystical.", "fields": "Spirituality, Research, Philosophy, Occult Sciences, Healing", "strengths": "exceptional intuition, deep wisdom, spiritual mastery", "challenges": "practical grounding, avoiding isolation"},
    (7,8): {"general": "Mulank 7 wisdom with Bhagyank 8 ambition. Analytical achievers who build through insight.", "fields": "Investment Analysis, Strategic Consulting, Research Management, Technology Leadership, Finance", "strengths": "deep analytical business sense, intuitive strategy, wise authority", "challenges": "social engagement, work-life balance"},
    (7,9): {"general": "Mulank 7 spirituality with Bhagyank 9 service. Wise humanitarians and spiritual teachers.", "fields": "Spiritual Teaching, Philosophy, International Aid, Healing Centers, Metaphysical Writing", "strengths": "wise compassion, spiritual service, deep understanding", "challenges": "practical execution, grounding in material world"},
    (8,1): {"general": "Mulank 8 ambition with Bhagyank 1 leadership. Born for positions of ultimate power.", "fields": "Executive Leadership, Business Ownership, Investment, Politics, Real Estate", "strengths": "decisive authority, financial mastery, pioneering ambition", "challenges": "work-life balance, collaboration"},
    (8,2): {"general": "Mulank 8 power with Bhagyank 2 diplomacy. Powerful yet emotionally intelligent leaders.", "fields": "Diplomatic Business, HR Leadership, Financial Counseling, Luxury Services, Mediation", "strengths": "emotionally intelligent authority, diplomatic power, relationship-based business", "challenges": "decisiveness, balancing sensitivity with ambition"},
    (8,3): {"general": "Mulank 8 achievement with Bhagyank 3 creativity. Ambitious creative entrepreneurs.", "fields": "Entertainment Business, Publishing, Brand Management, Creative Agency, Media", "strengths": "creative business mastery, charismatic authority, expressive ambition", "challenges": "focus, avoiding overcommitment"},
    (8,4): {"general": "Mulank 8 power with Bhagyank 4 discipline. Ultimate business builders and financial masters.", "fields": "Finance, Real Estate, Corporate Strategy, Engineering, Investment Management", "strengths": "exceptional financial discipline, strategic planning, powerful execution", "challenges": "flexibility, interpersonal warmth"},
    (8,5): {"general": "Mulank 8 ambition with Bhagyank 5 freedom. Dynamic business builders who adapt and conquer.", "fields": "Sales Leadership, Business Development, Entrepreneurship, Technology, Media", "strengths": "adaptable ambition, powerful communication, dynamic business sense", "challenges": "consistency, avoiding scattered focus"},
    (8,6): {"general": "Mulank 8 authority with Bhagyank 6 nurturing. Powerful leaders who build caring organizations.", "fields": "Healthcare Business, Education Leadership, Social Enterprise, Luxury Brand, Real Estate", "strengths": "powerful nurturing, responsible authority, aesthetic business vision", "challenges": "personal boundaries, avoiding martyrdom"},
    (8,7): {"general": "Mulank 8 ambition with Bhagyank 7 wisdom. Strategic achievers with deep analytical insight.", "fields": "Investment Analysis, Strategic Consulting, Technology Leadership, Research Management, Finance", "strengths": "analytical authority, wise strategy, deep business acumen", "challenges": "social engagement, sharing insights"},
    (8,8): {"general": "Double Saturn energy — extraordinary material ambition, discipline and financial power.", "fields": "Finance, Real Estate, Corporate Leadership, Investment, Business Empire Building", "strengths": "exceptional financial mastery, powerful discipline, material achievement", "challenges": "personal relationships, avoiding ruthlessness"},
    (8,9): {"general": "Mulank 8 power with Bhagyank 9 service. Powerful humanitarians who fund and lead great causes.", "fields": "Philanthropic Leadership, Social Enterprise, NGO Management, Political Service, Impact Investment", "strengths": "powerful compassion, resource-driven service, ambitious humanitarianism", "challenges": "personal boundaries, avoiding martyrdom"},
    (9,1): {"general": "Mulank 9 passion with Bhagyank 1 leadership. Courageous leaders who inspire and transform.", "fields": "Social Leadership, Military, Sports, Entrepreneurship, Activism", "strengths": "passionate leadership, courageous pioneering, inspiring ambition", "challenges": "patience, avoiding aggression"},
    (9,2): {"general": "Mulank 9 energy with Bhagyank 2 harmony. Passionate diplomats who serve with sensitivity.", "fields": "Diplomacy, Conflict Resolution, Social Work, Sports Coaching, Community Leadership", "strengths": "passionate empathy, diplomatic energy, harmonious service", "challenges": "channeling aggression, emotional boundaries"},
    (9,3): {"general": "Mulank 9 fire with Bhagyank 3 creativity. Inspirational creative forces.", "fields": "Motivational Speaking, Creative Arts, Entertainment, Activism, Media", "strengths": "passionate creativity, inspirational communication, energetic expression", "challenges": "focus, avoiding impulsiveness"},
    (9,4): {"general": "Mulank 9 drive with Bhagyank 4 discipline. Systematic warriors who achieve through hard work.", "fields": "Military, Sports Training, Social Reform, Engineering, Community Building", "strengths": "disciplined passion, systematic drive, practical courage", "challenges": "flexibility, work-life balance"},
    (9,5): {"general": "Mulank 9 energy with Bhagyank 5 freedom. Dynamic, adventurous humanitarians.", "fields": "Social Activism, Travel, International Aid, Journalism, Sports", "strengths": "passionate adaptability, energetic communication, adventurous service", "challenges": "commitment, avoiding impulsiveness"},
    (9,6): {"general": "Mulank 9 passion with Bhagyank 6 love. Passionate caregivers who fight for others.", "fields": "Healthcare, Social Work, Education, Advocacy, Community Service", "strengths": "passionate nurturing, courageous care, loving service", "challenges": "personal boundaries, channeling anger productively"},
    (9,7): {"general": "Mulank 9 energy with Bhagyank 7 wisdom. Passionate spiritual warriors and wise teachers.", "fields": "Spiritual Activism, Philosophy, Healing Arts, Military History, Social Research", "strengths": "passionate wisdom, spiritual courage, energetic insight", "challenges": "patience, practical grounding"},
    (9,8): {"general": "Mulank 9 fire with Bhagyank 8 ambition. Intense achievers driven by passion and power.", "fields": "Business Leadership, Sports Management, Military, Finance, Social Enterprise", "strengths": "passionate ambition, courageous authority, intense achievement", "challenges": "anger management, work-life balance"},
    (9,9): {"general": "Double Mars energy — extraordinary passion, courage and humanitarian drive.", "fields": "Humanitarian Leadership, Military Service, Sports, Activism, Social Reform", "strengths": "exceptional courage, passionate service, powerful transformation", "challenges": "channeling aggression, practical sustainability"},
}

# ── Helper ─────────────────────────────────────────────────────────────────────

def build_report(name, dob_str):
    """Parse DOB and run all calculations, returning enriched report dict."""
    parts = dob_str.split('-')
    if len(parts[0]) == 4:  # YYYY-MM-DD format from HTML date input
        year, month, day = (int(x) for x in parts)
    else:  # DD-MM-YYYY format
        day, month, year = (int(x) for x in parts)
    data = calculate_all(name, day, month, year)

    mulank = data['mulank']
    bhagyank = data['bhagyank']

    # Clamp master numbers to 9 for dict lookups
    def safe_key(n):
        if n in (11, 22, 33):
            return n % 9 or 9
        return n

    mk = safe_key(mulank)
    bk = safe_key(bhagyank)

    py = data['personal_year']
    pyk = safe_key(py)

    conn = data['connection']
    connk = safe_key(conn)

    pers = data['personality']
    persk = safe_key(pers)

    su = data['soul_urge']
    suk = safe_key(su)

    suc = data['success']
    suck = safe_key(suc)

    mat = data['maturity']
    matk = safe_key(mat)

    grid = data['grid']
    missing = data['missing']
    first_letter = data['first_letter']

    # Build Lo Shu interpretations for present numbers
    loshu_interps = {}
    for digit, count in grid.items():
        if count > 0:
            capped = min(count, 3)
            loshu_interps[digit] = LOSHU_INTERPRETATIONS[digit][capped]

    # Personal year luck for this mulank
    py_data = PERSONAL_YEAR_DATA[pyk]
    luck_key = f"M{mk}"
    luck_pct = py_data['luck'].get(luck_key, 70)

    # Career
    career_key = (mk, bk)
    career = CAREER_DATA.get(career_key, {
        "general": f"Mulank {mulank} and Bhagyank {bhagyank} combine leadership with purpose.",
        "fields": "Business, Consulting, Management, Service Industries",
        "strengths": "determination, adaptability, purpose-driven work",
        "challenges": "balance between personal goals and service"
    })

    report = {
        **data,
        'mulank_data': MULANK_DATA[mk],
        'bhagyank_text': BHAGYANK_DATA[bk],
        'love_sex_text': LOVE_SEX_DATA[bk],
        'connection_text': CONNECTION_DATA[connk],
        'personality_text': PERSONALITY_DATA[persk],
        'soul_urge_text': SOUL_URGE_DATA[suk],
        'first_letter_text': FIRST_LETTER_DATA.get(first_letter, "A unique individual with special gifts and qualities all your own."),
        'success_data': SUCCESS_DATA[suck],
        'maturity_text': MATURITY_DATA[matk],
        'personal_year_data': py_data,
        'personal_year_luck': luck_pct,
        'career': career,
        'loshu_interps': loshu_interps,
        'missing_data': {n: MISSING_NUMBER_DATA[n] for n in missing if n in MISSING_NUMBER_DATA},
    }
    return report


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate-report', methods=['POST'])
def generate_report():
    body = request.get_json()
    name = body.get('name', '').strip()
    dob = body.get('dob', '').strip()
    if not name or not dob:
        return jsonify({'error': 'Name and date of birth are required'}), 400
    try:
        report = build_report(name, dob)
        # Convert grid keys to strings for JSON
        report['grid'] = {str(k): v for k, v in report['grid'].items()}
        report['loshu_rows'] = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
        # Convert loshu_interps keys to strings
        report['loshu_interps'] = {str(k): v for k, v in report['loshu_interps'].items()}
        # Convert missing_data keys to strings
        report['missing_data'] = {str(k): v for k, v in report['missing_data'].items()}
        return jsonify(report)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    body = request.get_json()
    name = body.get('name', '').strip()
    dob = body.get('dob', '').strip()
    if not name or not dob:
        return jsonify({'error': 'Name and date of birth are required'}), 400

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        report = build_report(name, dob)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=20 * mm, leftMargin=20 * mm,
                                topMargin=20 * mm, bottomMargin=20 * mm)

        styles = getSampleStyleSheet()
        gold = colors.HexColor('#f5a623')
        dark_brown = colors.HexColor('#8B4513')
        cream = colors.HexColor('#FFF8F0')

        title_style = ParagraphStyle('Title', parent=styles['Title'],
                                     textColor=dark_brown, fontSize=24, spaceAfter=6,
                                     alignment=TA_CENTER)
        h1_style = ParagraphStyle('H1', parent=styles['Heading1'],
                                  textColor=dark_brown, fontSize=14, spaceAfter=4,
                                  spaceBefore=12)
        h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
                                  textColor=colors.HexColor('#D4A017'), fontSize=12,
                                  spaceAfter=3, spaceBefore=8)
        body_style = ParagraphStyle('Body', parent=styles['Normal'],
                                    fontSize=10, spaceAfter=6, leading=15)

        story = []

        # Title
        story.append(Paragraph("Numerology Report", title_style))
        story.append(Paragraph(
            f"<b>{report['name']}</b> — DOB: {report['dob']}",
            ParagraphStyle('sub', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12, spaceAfter=4)
        ))
        story.append(HRFlowable(width="100%", thickness=2, color=gold))
        story.append(Spacer(1, 6 * mm))

        # Numbers summary table
        nums = [
            ['Mulank', str(report['mulank']), 'Bhagyank', str(report['bhagyank'])],
            ['Connection', str(report['connection']), 'Personality', str(report['personality'])],
            ['Soul Urge', str(report['soul_urge']), 'Success', str(report['success'])],
            ['Maturity', str(report['maturity']), 'Personal Year', str(report['personal_year'])],
        ]
        t = Table(nums, colWidths=[45 * mm, 25 * mm, 45 * mm, 25 * mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), cream),
            ('TEXTCOLOR', (0, 0), (-1, -1), dark_brown),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, gold),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [cream, colors.HexColor('#FFF0D8')]),
            ('FONTSIZE', (1, 0), (1, -1), 12),
            ('FONTSIZE', (3, 0), (3, -1), 12),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
        ]))
        story.append(t)
        story.append(Spacer(1, 6 * mm))

        def section(title, content_paragraphs):
            story.append(HRFlowable(width="100%", thickness=1, color=gold))
            story.append(Paragraph(title, h1_style))
            for p in content_paragraphs:
                if p:
                    story.append(Paragraph(str(p), body_style))

        # 1. Mulank
        mk = report['mulank']
        bk = report['bhagyank']
        def format_mulank_para(p):
            for label in ['Favourable Period:', 'Unfavourable Period:', 'Lucky Colours:']:
                if p.startswith(label):
                    rest = p[len(label):].strip()
                    return f'<font size="12"><b>{label}</b></font> {rest}'
            return p
        mulank_pdf_paras = [format_mulank_para(p) for p in MULANK_PDF_DATA[mk].split('\n') if p.strip()]
        section(f"1. {report['mulank_data']['title']}", mulank_pdf_paras)

        # 2. Bhagyank
        bhagyank_pdf_paras = [p for p in BHAGYANK_PDF_DATA[bk].split('\n') if p.strip()]
        section(f"2. Bhagyank {report['bhagyank']} — Destiny Number", bhagyank_pdf_paras)

        # 3. Love & Sex
        love_sex_pdf_paras = [p for p in LOVE_SEX_PDF_DATA[bk].split('\n') if p.strip()]
        section("3. Love & Sex Style", love_sex_pdf_paras)

        # 4. Connection Number
        section(f"4. Connection Number: {report['connection']}", [
            report['connection_text'],
        ])

        # 5. Personality Number
        section(f"5. Personality Number: {report['personality']}", [
            report['personality_text'],
        ])

        # 6. Soul Urge Number
        su_lines = report['soul_urge_text'].split('.')
        section(f"6. Soul Urge Number: {report['soul_urge']}", [
            report['soul_urge_text'],
        ])

        # 7. First Letter
        section(f"7. First Letter of Name: {report['first_letter']}", [
            report['first_letter_text'],
        ])

        # 8. Success Number
        sd = report['success_data']
        section(f"8. Success Number: {report['success']}", [
            f"<font size=\"11\"><b>Qualities</b></font>",
            sd['qualities'],
            f"<font size=\"11\"><b>Challenges</b></font>",
            sd['challenges'],
        ])

        # 9. Maturity Number
        section(f"9. Maturity Number: {report['maturity']}", [
            report['maturity_text'],
        ])

        # 10. Personal Year
        pyd = report['personal_year_data']
        section(f"10. Personal Year {report['personal_year']} ({report['current_year']})", [
            f"<font size=\"11\"><b>{pyd['title']}</b></font>",
            f"<font size=\"11\"><b>Positive Results</b></font>",
            pyd['positive'],
            f"<font size=\"11\"><b>Negative Results</b></font>",
            pyd['negative'],
            f"<font size=\"11\"><b>Your Luck This Year: {report['personal_year_luck']}%</b></font>",
        ])

        # 11. Career
        car = report['career']
        section(f"11. Career Numerology (Mulank {report['mulank']} + Bhagyank {report['bhagyank']})", [
            car['general'],
            f"<font size=\"11\"><b>Recommended Career Fields</b></font>",
            car['fields'],
            f"<font size=\"11\"><b>Key Strengths</b></font>",
            car['strengths'],
            f"<font size=\"11\"><b>Challenges to Overcome</b></font>",
            car['challenges'],
        ])

        # 12. Lo Shu Grid
        story.append(HRFlowable(width="100%", thickness=1, color=gold))
        story.append(Paragraph("12. Lo Shu Grid", h1_style))

        grid = report['grid']
        loshu_rows = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
        grid_data = []
        for row in loshu_rows:
            grid_row = []
            for num in row:
                count = grid.get(str(num), grid.get(num, 0))
                if count > 0:
                    grid_row.append(' '.join([str(num)] * count))
                else:
                    grid_row.append(f"{num}")
            grid_data.append(grid_row)

        gt = Table(grid_data, colWidths=[30 * mm, 30 * mm, 30 * mm])
        gt_style = [
            ('FONTSIZE', (0, 0), (-1, -1), 16),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1.5, gold),
            ('ROWHEIGHT', (0, 0), (-1, -1), 30 * mm),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]

        for r_idx, row in enumerate(loshu_rows):
            for c_idx, num in enumerate(row):
                count = grid.get(str(num), grid.get(num, 0))
                if count > 0:
                    gt_style.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), gold))
                    gt_style.append(('TEXTCOLOR', (c_idx, r_idx), (c_idx, r_idx), colors.black))
                else:
                    gt_style.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor('#e0e0e0')))
                    gt_style.append(('TEXTCOLOR', (c_idx, r_idx), (c_idx, r_idx), colors.grey))

        gt.setStyle(TableStyle(gt_style))
        story.append(gt)
        story.append(Spacer(1, 4 * mm))

        # Lo Shu interpretations
        for digit, interp in sorted(report['loshu_interps'].items()):
            story.append(Paragraph(f"<b>Number {digit}:</b> {interp}", body_style))

        # 13. Missing Numbers
        story.append(HRFlowable(width="100%", thickness=1, color=gold))
        story.append(Paragraph("13. Missing Numbers — Impact & Remedy", h1_style))

        if report['missing']:
            for num in report['missing']:
                mn = MISSING_NUMBER_DATA.get(num)
                if mn:
                    story.append(Paragraph(f"<b>Missing Number {num}:</b>", h2_style))
                    story.append(Paragraph(f"<b>Impact:</b> {mn['impact']}", body_style))
                    story.append(Paragraph(f"<b>Remedy ({mn['remedy_day']}):</b> {mn['remedy']}", body_style))
        else:
            story.append(Paragraph(
                "All numbers 1-9 are present in your date of birth. You are blessed with a complete Lo Shu Grid!",
                body_style))

        story.append(Spacer(1, 8 * mm))
        story.append(HRFlowable(width="100%", thickness=2, color=gold))
        story.append(Paragraph(
            "Report generated with Numerology Report App",
            ParagraphStyle('footer', parent=styles['Normal'],
                           alignment=TA_CENTER, textColor=colors.grey, fontSize=9)
        ))

        doc.build(story)
        buffer.seek(0)

        response = make_response(buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        safe_name = name.replace(' ', '_')
        response.headers['Content-Disposition'] = f'attachment; filename=numerology_{safe_name}.pdf'
        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)
