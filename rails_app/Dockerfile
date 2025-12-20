FROM ruby:3.3.0-slim

WORKDIR /rails

# Install system dependencies
RUN apt-get update -qq && \
    apt-get install -y build-essential libpq-dev curl git && \
    rm -rf /var/lib/apt/lists/*

# Gems
COPY Gemfile* .
RUN bundle install

# Entrypoint to handle migration/server
COPY ./bin/docker-entrypoint /rails/bin/
RUN chmod +x /rails/bin/docker-entrypoint

ENTRYPOINT ["/rails/bin/docker-entrypoint"]

EXPOSE 3000
CMD ["./bin/rails", "server", "-b", "0.0.0.0"]
