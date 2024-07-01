import React, {useEffect, useState} from 'react';

const CourseInfo = () => {
    const [courseData, setCourseData] = useState(null);

    useEffect(() => {
        fetch('http://127.0.0.1:8000/courses?page=2')
            .then(response => response.json())
            .then(data => setCourseData(data));
    }, []);

    if (!courseData) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <ul>
                {courseData.results.map(course => (
                    <li key={course.id}>
                        <h4>{course.title}</h4>
                        <p>Description: {course.description}</p>
                        <ul>
                            {course.seasons.map((season, index) => (
                                <li key={season.id}>
                                    {index + 1}st season: {season.title}
                                    <ul>
                                        {course.lectures.filter(lecture => lecture.season_title === season.title)
                                            .map((filteredLecture, lectureIndex) => (
                                                <li key={filteredLecture.id}>
                                                    Lecture {lectureIndex}: {filteredLecture.title}
                                                </li>
                                            ))}
                                    </ul>
                                </li>
                            ))}
                        </ul>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default CourseInfo;
