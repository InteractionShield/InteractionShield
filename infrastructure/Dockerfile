FROM ubuntu:jammy

RUN apt-get update && \
    apt-get install -y \
    bash curl make wget unzip yacc zip \
    openjdk-8-jdk \
    python3 python3-pip \
    qtbase5-dev \
    libxcb-cursor0 \
    libxkbcommon-x11-0 \
    libegl1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV GROOVY_HOME=/opt/groovy-4.0.22
ENV PATH=$JAVA_HOME/bin:$GROOVY_HOME/bin:$PATH

RUN cd /usr/bin && \
    ln -sf /usr/bin/python3 /usr/local/bin/python && \
    pip3 --no-cache-dir install --upgrade pip 

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

RUN curl -L "https://groovy.jfrog.io/ui/api/v1/download?repoKey=dist-release-local&path=groovy-zips%252Fapache-groovy-sdk-4.0.22.zip&isNativeBrowsing=true" -o groovy.zip && \
unzip -q groovy.zip -d /opt && \
ln -s /opt/groovy-4.0.22/bin/groovyc /bin/groovyc && \
ln -s /opt/groovy-4.0.22/bin/groovy /bin/groovy

RUN curl -L "https://spinroot.com/spin/Archive/spin646.tar.gz" -o spin.tar.gz && \
tar -xvzf spin.tar.gz -C /opt && \
cd /opt/Spin/Src6.4.6 && \
make && \
ln -s /opt/Spin/Src6.4.6/spin /bin/spin

RUN curl -L "https://www.dropbox.com/scl/fi/5eegtfkvmrkpe9ln5se0o/InteractionShield.tar.gz?rlkey=nqer471q9496jukaxlbj5vabu&st=2t7tx19h&dl=0" -o /opt/InteractionShield.tar.gz

WORKDIR /InteractionShield

CMD ["bash"]
